"""Stream quality analyzer - extract and analyze stream quality metrics."""
import asyncio
import json
import logging
import re
from typing import Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class QualityAnalyzer:
    """Analyze stream quality using FFprobe and URL analysis."""

    # Resolution priorities (higher = better)
    RESOLUTION_PRIORITY = {
        "8K": 1000,
        "4K": 900,
        "2160p": 900,
        "1440p": 800,
        "QHD": 800,
        "1080p": 700,
        "FHD": 700,
        "720p": 600,
        "HD": 600,
        "576p": 500,
        "480p": 400,
        "SD": 300,
        "360p": 200,
        "240p": 100,
    }

    # Minimum bitrates for quality levels (kbps)
    QUALITY_BITRATES = {
        "4K": 15000,
        "1080p": 5000,
        "720p": 2500,
        "480p": 1000,
        "360p": 500,
    }

    def __init__(self, enable_bitrate_analysis: bool = True, ffprobe_timeout: int = 15):
        """
        Initialize quality analyzer.

        Args:
            enable_bitrate_analysis: Whether to analyze bitrate with FFprobe
            ffprobe_timeout: Timeout for FFprobe analysis in seconds
        """
        self.enable_bitrate_analysis = enable_bitrate_analysis
        self.ffprobe_timeout = ffprobe_timeout

    def extract_resolution_from_name(self, name: str) -> Optional[str]:
        """
        Extract resolution from channel/stream name.

        Args:
            name: Channel or stream name

        Returns:
            Resolution string or None
        """
        name_upper = name.upper()

        # Check for explicit resolution indicators
        for resolution in self.RESOLUTION_PRIORITY.keys():
            # Match as whole word or at end of string
            pattern = r'\b' + re.escape(resolution) + r'\b'
            if re.search(pattern, name_upper):
                return resolution

        return None

    def extract_resolution_from_url(self, url: str) -> Optional[str]:
        """
        Extract resolution from stream URL.

        Args:
            url: Stream URL

        Returns:
            Resolution string or None
        """
        url_upper = url.upper()

        # Check URL for resolution indicators
        for resolution in self.RESOLUTION_PRIORITY.keys():
            if resolution in url_upper:
                return resolution

        return None

    async def analyze_stream(self, stream_url: str, stream_name: Optional[str] = None,
                            quick_mode: bool = False) -> Dict:
        """
        Analyze stream quality.

        Args:
            stream_url: Stream URL
            stream_name: Optional stream name for name-based detection
            quick_mode: If True, skip FFprobe analysis

        Returns:
            Dictionary with quality metrics
        """
        result = {
            "resolution": None,
            "bitrate": None,
            "codec": None,
            "fps": None,
            "quality_score": 0,
            "analysis_method": "none"
        }

        # Try to extract from name first (fastest)
        if stream_name:
            resolution = self.extract_resolution_from_name(stream_name)
            if resolution:
                result["resolution"] = resolution
                result["quality_score"] = self.RESOLUTION_PRIORITY.get(resolution, 0)
                result["analysis_method"] = "name"

        # Try to extract from URL
        if not result["resolution"]:
            resolution = self.extract_resolution_from_url(stream_url)
            if resolution:
                result["resolution"] = resolution
                result["quality_score"] = self.RESOLUTION_PRIORITY.get(resolution, 0)
                result["analysis_method"] = "url"

        # Analyze with FFprobe if enabled and not in quick mode
        if self.enable_bitrate_analysis and not quick_mode:
            ffprobe_result = await self._analyze_with_ffprobe(stream_url)
            if ffprobe_result:
                result.update(ffprobe_result)
                result["analysis_method"] = "ffprobe"

                # Calculate quality score based on bitrate and resolution
                result["quality_score"] = self._calculate_quality_score(
                    result["resolution"],
                    result["bitrate"]
                )

        return result

    async def _analyze_with_ffprobe(self, stream_url: str) -> Optional[Dict]:
        """
        Analyze stream using FFprobe.

        Args:
            stream_url: Stream URL

        Returns:
            Dictionary with stream info or None if analysis fails
        """
        try:
            # Build ffprobe command
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",  # Select first video stream
                "-show_entries", "stream=codec_name,width,height,bit_rate,r_frame_rate",
                "-show_entries", "format=bit_rate,duration",
                "-of", "json",
                "-timeout", str(self.ffprobe_timeout * 1000000),  # microseconds
                "-analyzeduration", "5000000",  # 5 seconds
                "-probesize", "5000000",  # 5MB
                stream_url
            ]

            # Run ffprobe
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.ffprobe_timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                logger.debug(f"FFprobe timeout for {stream_url}")
                return None

            if process.returncode != 0:
                logger.debug(f"FFprobe failed for {stream_url}: {stderr.decode()}")
                return None

            # Parse output
            data = json.loads(stdout.decode())

            result = {}

            # Extract video stream info
            if "streams" in data and len(data["streams"]) > 0:
                stream = data["streams"][0]

                # Codec
                result["codec"] = stream.get("codec_name")

                # Resolution
                width = stream.get("width")
                height = stream.get("height")
                if width and height:
                    result["resolution"] = self._height_to_resolution(height)

                # FPS
                fps_str = stream.get("r_frame_rate", "")
                if fps_str and "/" in fps_str:
                    num, den = fps_str.split("/")
                    result["fps"] = float(num) / float(den) if float(den) > 0 else None

                # Bitrate from stream
                bitrate = stream.get("bit_rate")
                if bitrate:
                    result["bitrate"] = int(int(bitrate) / 1000)  # Convert to kbps

            # Extract format info (fallback for bitrate)
            if "format" in data and not result.get("bitrate"):
                bitrate = data["format"].get("bit_rate")
                if bitrate:
                    result["bitrate"] = int(int(bitrate) / 1000)  # Convert to kbps

            return result if result else None

        except Exception as e:
            logger.debug(f"FFprobe analysis failed for {stream_url}: {str(e)}")
            return None

    def _height_to_resolution(self, height: int) -> str:
        """
        Convert video height to resolution string.

        Args:
            height: Video height in pixels

        Returns:
            Resolution string
        """
        if height >= 2160:
            return "4K"
        elif height >= 1440:
            return "1440p"
        elif height >= 1080:
            return "1080p"
        elif height >= 720:
            return "720p"
        elif height >= 576:
            return "576p"
        elif height >= 480:
            return "480p"
        elif height >= 360:
            return "360p"
        else:
            return "SD"

    def _calculate_quality_score(self, resolution: Optional[str],
                                 bitrate: Optional[int]) -> int:
        """
        Calculate overall quality score.

        Args:
            resolution: Resolution string
            bitrate: Bitrate in kbps

        Returns:
            Quality score (0-1000, higher is better)
        """
        score = 0

        # Base score from resolution
        if resolution:
            score = self.RESOLUTION_PRIORITY.get(resolution, 0)

        # Adjust based on bitrate
        if bitrate:
            # Check if bitrate is appropriate for resolution
            expected_bitrate = self._get_expected_bitrate(resolution)
            if expected_bitrate:
                # Bonus if bitrate meets or exceeds expected
                if bitrate >= expected_bitrate:
                    score += 50
                else:
                    # Penalty if bitrate is too low
                    ratio = bitrate / expected_bitrate
                    score = int(score * ratio)

        return score

    def _get_expected_bitrate(self, resolution: Optional[str]) -> Optional[int]:
        """
        Get expected minimum bitrate for resolution.

        Args:
            resolution: Resolution string

        Returns:
            Expected bitrate in kbps or None
        """
        if not resolution:
            return None

        # Map resolution to quality level
        if resolution in ["4K", "2160p"]:
            return self.QUALITY_BITRATES.get("4K")
        elif resolution in ["1080p", "FHD"]:
            return self.QUALITY_BITRATES.get("1080p")
        elif resolution in ["720p", "HD"]:
            return self.QUALITY_BITRATES.get("720p")
        elif resolution in ["480p", "SD"]:
            return self.QUALITY_BITRATES.get("480p")
        elif resolution in ["360p", "240p"]:
            return self.QUALITY_BITRATES.get("360p")

        return None

    def compare_streams(self, stream1: Dict, stream2: Dict) -> int:
        """
        Compare two streams by quality.

        Args:
            stream1: First stream quality metrics
            stream2: Second stream quality metrics

        Returns:
            -1 if stream1 is better, 1 if stream2 is better, 0 if equal
        """
        score1 = stream1.get("quality_score", 0)
        score2 = stream2.get("quality_score", 0)

        if score1 > score2:
            return -1
        elif score1 < score2:
            return 1
        else:
            return 0

    def sort_streams_by_quality(self, streams: list) -> list:
        """
        Sort streams by quality (best first).

        Args:
            streams: List of streams with quality_score

        Returns:
            Sorted list of streams
        """
        return sorted(streams, key=lambda x: x.get("quality_score", 0), reverse=True)
