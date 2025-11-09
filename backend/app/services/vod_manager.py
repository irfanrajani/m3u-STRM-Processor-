"""VOD manager - generate .strm files for Emby."""
import os
import re
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class VODManager:
    """Manage VOD content and generate .strm files for Emby."""

    def __init__(self, output_dir: str):
        """
        Initialize VOD manager.

        Args:
            output_dir: Base directory for .strm files
        """
        self.output_dir = Path(output_dir)
        self.movies_dir = self.output_dir / "Movies"
        self.series_dir = self.output_dir / "TV Shows"

        # Create directories
        self.movies_dir.mkdir(parents=True, exist_ok=True)
        self.series_dir.mkdir(parents=True, exist_ok=True)

    def sanitize_filename(self, name: str) -> str:
        """
        Sanitize filename by removing invalid characters.

        Args:
            name: Original filename

        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')

        # Replace multiple spaces with single space
        name = re.sub(r'\s+', ' ', name)

        # Trim and limit length
        name = name.strip()[:200]

        return name

    def generate_movie_strm(self, movie: Dict) -> Optional[str]:
        """
        Generate .strm file for a movie.

        Args:
            movie: Movie dictionary with title, year, stream_url, genre, etc.

        Returns:
            Path to generated .strm file or None if failed
        """
        try:
            title = movie.get("title", "Unknown")
            year = movie.get("year")
            stream_url = movie.get("stream_url")
            genre = movie.get("genre", "Unknown")

            if not stream_url:
                logger.error(f"No stream URL for movie: {title}")
                return None

            # Sanitize title
            safe_title = self.sanitize_filename(title)

            # Create folder name: "Movie Title (Year)"
            if year:
                folder_name = f"{safe_title} ({year})"
            else:
                folder_name = safe_title

            # Create genre folder
            safe_genre = self.sanitize_filename(genre)
            genre_dir = self.movies_dir / safe_genre
            genre_dir.mkdir(parents=True, exist_ok=True)

            # Create movie folder
            movie_dir = genre_dir / folder_name
            movie_dir.mkdir(parents=True, exist_ok=True)

            # Create .strm filename
            strm_filename = f"{folder_name}.strm"
            strm_path = movie_dir / strm_filename

            # Write stream URL to .strm file
            with open(strm_path, 'w', encoding='utf-8') as f:
                f.write(stream_url)

            logger.info(f"Generated .strm file: {strm_path}")
            return str(strm_path)

        except Exception as e:
            logger.error(f"Failed to generate .strm for movie {movie.get('title')}: {str(e)}")
            return None

    def generate_episode_strm(self, series: Dict, episode: Dict) -> Optional[str]:
        """
        Generate .strm file for a TV episode.

        Args:
            series: Series dictionary with title, year, genre, etc.
            episode: Episode dictionary with season, episode, title, stream_url

        Returns:
            Path to generated .strm file or None if failed
        """
        try:
            series_title = series.get("title", "Unknown")
            series_year = series.get("year")
            genre = series.get("genre", "Unknown")

            season_num = episode.get("season_number")
            episode_num = episode.get("episode_number")
            episode_title = episode.get("title", f"Episode {episode_num}")
            stream_url = episode.get("stream_url")

            if not stream_url or season_num is None or episode_num is None:
                logger.error(f"Missing required data for episode: {series_title}")
                return None

            # Sanitize series title
            safe_series_title = self.sanitize_filename(series_title)

            # Create folder structure: Genre/Series Title (Year)/Season XX/
            if series_year:
                series_folder = f"{safe_series_title} ({series_year})"
            else:
                series_folder = safe_series_title

            safe_genre = self.sanitize_filename(genre)
            genre_dir = self.series_dir / safe_genre
            series_dir = genre_dir / series_folder
            season_dir = series_dir / f"Season {season_num:02d}"

            # Create directories
            season_dir.mkdir(parents=True, exist_ok=True)

            # Create .strm filename: "Series - S01E05 - Episode Title.strm"
            safe_episode_title = self.sanitize_filename(episode_title)
            strm_filename = f"{safe_series_title} - S{season_num:02d}E{episode_num:02d} - {safe_episode_title}.strm"
            strm_path = season_dir / strm_filename

            # Write stream URL to .strm file
            with open(strm_path, 'w', encoding='utf-8') as f:
                f.write(stream_url)

            logger.info(f"Generated .strm file: {strm_path}")
            return str(strm_path)

        except Exception as e:
            logger.error(f"Failed to generate .strm for episode {series.get('title')}: {str(e)}")
            return None

    def batch_generate_movies(self, movies: List[Dict]) -> Dict[str, int]:
        """
        Generate .strm files for multiple movies.

        Args:
            movies: List of movie dictionaries

        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0}

        for movie in movies:
            result = self.generate_movie_strm(movie)
            if result:
                results["success"] += 1
            else:
                results["failed"] += 1

        return results

    def batch_generate_series(self, series_list: List[Dict]) -> Dict[str, int]:
        """
        Generate .strm files for multiple series.

        Args:
            series_list: List of series dictionaries (each with episodes list)

        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0}

        for series in series_list:
            episodes = series.get("episodes", [])

            for episode in episodes:
                result = self.generate_episode_strm(series, episode)
                if result:
                    results["success"] += 1
                else:
                    results["failed"] += 1

        return results

    def cleanup_orphaned_files(self, active_movie_ids: List[int],
                               active_episode_ids: List[int]) -> int:
        """
        Remove .strm files for content that no longer exists.

        Args:
            active_movie_ids: List of active movie IDs
            active_episode_ids: List of active episode IDs

        Returns:
            Number of files removed
        """
        removed_count = 0

        # This would need to track which .strm files correspond to which IDs
        # For now, we'll leave this as a placeholder
        # In production, you'd maintain a mapping database

        logger.info(f"Cleanup removed {removed_count} orphaned files")
        return removed_count

    def get_stats(self) -> Dict:
        """
        Get statistics about generated .strm files.

        Returns:
            Dictionary with file counts
        """
        stats = {
            "total_movies": 0,
            "total_episodes": 0,
            "total_size_mb": 0
        }

        # Count movie files
        if self.movies_dir.exists():
            movie_files = list(self.movies_dir.rglob("*.strm"))
            stats["total_movies"] = len(movie_files)

        # Count episode files
        if self.series_dir.exists():
            episode_files = list(self.series_dir.rglob("*.strm"))
            stats["total_episodes"] = len(episode_files)

        # Calculate total size (strm files are tiny, but include them)
        all_files = list(self.output_dir.rglob("*.strm"))
        total_size = sum(f.stat().st_size for f in all_files if f.exists())
        stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)

        return stats

    def delete_movie_strm(self, strm_path: str) -> bool:
        """
        Delete a movie .strm file and its folder if empty.

        Args:
            strm_path: Path to .strm file

        Returns:
            True if successful
        """
        try:
            path = Path(strm_path)
            if path.exists():
                path.unlink()

                # Remove parent folder if empty
                parent = path.parent
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()

                return True
        except Exception as e:
            logger.error(f"Failed to delete .strm file {strm_path}: {str(e)}")

        return False

    def delete_episode_strm(self, strm_path: str) -> bool:
        """
        Delete an episode .strm file and cleanup empty folders.

        Args:
            strm_path: Path to .strm file

        Returns:
            True if successful
        """
        return self.delete_movie_strm(strm_path)  # Same logic
