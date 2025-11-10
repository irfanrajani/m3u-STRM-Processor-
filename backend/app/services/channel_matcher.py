"""Channel matcher service - intelligent channel matching with region/variant detection."""
import re
import logging
from typing import Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process
import imagehash
from PIL import Image
import httpx
from io import BytesIO

logger = logging.getLogger(__name__)


class ChannelMatcher:
    """Intelligent channel matching with fuzzy string matching and region awareness."""

    # Common region indicators
    REGIONS = [
        "east", "west", "north", "south", "central",
        "ontario", "quebec", "alberta", "bc", "atlantic",
        "pacific", "mountain", "eastern", "western",
        "usa", "us", "uk", "ca", "canadian", "american", "british"
    ]

    # Common variants
    VARIANTS = [
        "hd", "sd", "4k", "uhd", "fhd",
        "plus", "+", "premium", "extra",
        "1", "2", "3", "news", "sports", "movies"
    ]

    # Patterns to remove for normalization
    NOISE_PATTERNS = [
        r'\[.*?\]',  # Remove [brackets]
        r'\(.*?\)',  # Remove (parentheses)
        r'^\s*[|-]?\s*',  # Remove leading dashes/pipes
        r'\s*[|-]?\s*$',  # Remove trailing dashes/pipes
        r'\s+',  # Normalize whitespace
    ]

    def __init__(self, fuzzy_threshold: int = 85, enable_logo_matching: bool = True,
                 logo_threshold: int = 90):
        """
        Initialize channel matcher.

        Args:
            fuzzy_threshold: Minimum similarity score (0-100) for fuzzy matching
            enable_logo_matching: Whether to use logo image matching
            logo_threshold: Minimum similarity score for logo matching
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.enable_logo_matching = enable_logo_matching
        self.logo_threshold = logo_threshold
        self.logo_cache: Dict[str, str] = {}  # URL -> hash

    def normalize_name(self, name: str) -> str:
        """
        Normalize channel name for comparison.

        Args:
            name: Raw channel name

        Returns:
            Normalized name
        """
        if not name:
            return ""

        normalized = name.lower().strip()

        # Remove noise patterns
        for pattern in self.NOISE_PATTERNS:
            normalized = re.sub(pattern, ' ', normalized)

        # Normalize whitespace
        normalized = ' '.join(normalized.split())

        return normalized

    def extract_region(self, name: str) -> Optional[str]:
        """
        Extract region from channel name.

        Args:
            name: Channel name

        Returns:
            Region if found, None otherwise
        """
        normalized = name.lower()

        for region in self.REGIONS:
            # Look for region as separate word
            pattern = r'\b' + re.escape(region) + r'\b'
            if re.search(pattern, normalized):
                return region.capitalize()

        return None

    def extract_variant(self, name: str) -> Optional[str]:
        """
        Extract variant from channel name.

        Args:
            name: Channel name

        Returns:
            Variant if found, None otherwise
        """
        normalized = name.lower()

        for variant in self.VARIANTS:
            # Look for variant as separate word or attached
            pattern = r'\b' + re.escape(variant) + r'\b|' + re.escape(variant) + r'(?=\s|$)'
            if re.search(pattern, normalized):
                return variant.upper() if variant.isupper() or len(variant) <= 2 else variant.capitalize()

        return None

    def extract_base_name(self, name: str) -> str:
        """
        Extract base channel name without region/variant.

        Args:
            name: Channel name

        Returns:
            Base name
        """
        normalized = self.normalize_name(name)

        # Remove regions
        for region in self.REGIONS:
            pattern = r'\b' + re.escape(region) + r'\b'
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)

        # Remove variants
        for variant in self.VARIANTS:
            pattern = r'\b' + re.escape(variant) + r'\b|' + re.escape(variant) + r'(?=\s|$)'
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)

        # Clean up
        normalized = ' '.join(normalized.split()).strip()

        return normalized

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity score between two channel names.

        Args:
            name1: First channel name
            name2: Second channel name

        Returns:
            Similarity score (0-100)
        """
        # Normalize names
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)

        # Try multiple similarity metrics and use the highest
        scores = [
            fuzz.ratio(norm1, norm2),
            fuzz.partial_ratio(norm1, norm2),
            fuzz.token_sort_ratio(norm1, norm2),
            fuzz.token_set_ratio(norm1, norm2),
        ]

        return max(scores)

    def is_same_channel(self, name1: str, name2: str, region1: Optional[str] = None,
                        region2: Optional[str] = None, variant1: Optional[str] = None,
                        variant2: Optional[str] = None) -> bool:
        """
        Determine if two channels are the same.

        Args:
            name1: First channel name
            name2: Second channel name
            region1: First channel region
            region2: Second channel region
            variant1: First channel variant
            variant2: Second channel variant

        Returns:
            True if channels are considered the same
        """
        # Extract base names
        base1 = self.extract_base_name(name1)
        base2 = self.extract_base_name(name2)

        # Check base name similarity
        similarity = self.calculate_similarity(base1, base2)

        if similarity < self.fuzzy_threshold:
            return False

        # Extract regions and variants if not provided
        if region1 is None:
            region1 = self.extract_region(name1)
        if region2 is None:
            region2 = self.extract_region(name2)
        if variant1 is None:
            variant1 = self.extract_variant(name1)
        if variant2 is None:
            variant2 = self.extract_variant(name2)

        # Channels with different regions are different channels
        if region1 and region2 and region1.lower() != region2.lower():
            return False

        # Channels with different variants are different channels
        if variant1 and variant2 and variant1.lower() != variant2.lower():
            return False

        return True

    async def calculate_logo_similarity(self, logo_url1: Optional[str],
                                        logo_url2: Optional[str]) -> Optional[float]:
        """
        Calculate similarity between two logo images using perceptual hashing.

        Args:
            logo_url1: First logo URL
            logo_url2: Second logo URL

        Returns:
            Similarity score (0-100) or None if comparison fails
        """
        if not self.enable_logo_matching or not logo_url1 or not logo_url2:
            return None

        try:
            # Get or compute hashes
            hash1 = await self._get_image_hash(logo_url1)
            hash2 = await self._get_image_hash(logo_url2)

            if not hash1 or not hash2:
                return None

            # Calculate hamming distance
            distance = hash1 - hash2
            # Convert to similarity percentage (lower distance = higher similarity)
            similarity = max(0, 100 - (distance * 100 / 64))  # 64 is max distance for 8x8 hash

            return similarity

        except Exception as e:
            logger.debug(f"Logo comparison failed: {str(e)}")
            return None

    async def _get_image_hash(self, url: str) -> Optional[imagehash.ImageHash]:
        """
        Get perceptual hash of an image from URL.

        Args:
            url: Image URL

        Returns:
            Image hash or None if failed
        """
        # Check cache
        if url in self.logo_cache:
            try:
                return imagehash.hex_to_hash(self.logo_cache[url])
            except (ValueError, TypeError) as e:
                logger.debug(f"Invalid cached hash for {url}: {e}")
                del self.logo_cache[url]  # Remove invalid cache entry

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()

                image = Image.open(BytesIO(response.content))
                img_hash = imagehash.average_hash(image)

                # Cache the hash
                self.logo_cache[url] = str(img_hash)

                return img_hash

        except Exception as e:
            logger.debug(f"Failed to hash image {url}: {str(e)}")
            return None

    def find_best_match(self, channel_name: str, candidates: List[Dict],
                        region: Optional[str] = None,
                        variant: Optional[str] = None) -> Optional[Dict]:
        """
        Find the best matching channel from a list of candidates.

        Args:
            channel_name: Channel name to match
            candidates: List of candidate channels (must have 'name' key)
            region: Channel region
            variant: Channel variant

        Returns:
            Best matching channel or None
        """
        if not candidates:
            return None

        base_name = self.extract_base_name(channel_name)
        best_match = None
        best_score = 0

        for candidate in candidates:
            candidate_name = candidate.get("name", "")
            candidate_region = candidate.get("region") or self.extract_region(candidate_name)
            candidate_variant = candidate.get("variant") or self.extract_variant(candidate_name)

            # Check if same channel
            if not self.is_same_channel(channel_name, candidate_name, region,
                                        candidate_region, variant, candidate_variant):
                continue

            # Calculate score
            score = self.calculate_similarity(base_name, self.extract_base_name(candidate_name))

            if score > best_score:
                best_score = score
                best_match = candidate

        return best_match if best_score >= self.fuzzy_threshold else None
