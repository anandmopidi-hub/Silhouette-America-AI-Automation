import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
from playwright.sync_api import Page
from utils.common_helper import CommonHelper
from utils.logger import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = PROJECT_ROOT / "artifacts" / "videos"
PASSED_VIDEOS_DIR = VIDEOS_DIR / "passed"
FAILED_VIDEOS_DIR = VIDEOS_DIR / "failed"
SKIPPED_VIDEOS_DIR = VIDEOS_DIR / "skipped"
TEMP_VIDEOS_DIR = VIDEOS_DIR / "_temp"

CommonHelper.ensure_directory(PASSED_VIDEOS_DIR)
CommonHelper.ensure_directory(FAILED_VIDEOS_DIR)
CommonHelper.ensure_directory(SKIPPED_VIDEOS_DIR)
CommonHelper.ensure_directory(TEMP_VIDEOS_DIR)


class VideoHelper:
    """Centralized video recording management.

    Organizes video artifacts based on test result and configuration policy.
    """

    @classmethod
    def get_temp_video_dir(cls) -> Path:
        """Directory configured in BrowserContext for recording raw video."""
        CommonHelper.ensure_directory(TEMP_VIDEOS_DIR)
        return TEMP_VIDEOS_DIR

    @classmethod
    def process_test_video(
        cls,
        page: Optional[Page] = None,
        test_name: str = "",
        status: str = "passed",
        video_mode: str = "retain-on-failure",
        pages: Optional[List[Page]] = None,
    ) -> Optional[Path]:
        """Process and move the recorded video for a completed test.

        Supports both single-page tests and multi-page/popup flows by concatenating
        all recorded page interactions into a unified video.

        Args:
            page: Primary Playwright Page instance.
            test_name: Name of the test being processed.
            status: Outcome of the test ('passed', 'failed', 'skipped').
            video_mode: Configured mode ('on', 'off', 'retain-on-failure').
            pages: Optional list of all Page instances created during the test.

        Returns:
            Path to the saved video file or None.
        """
        if video_mode == "off":
            return None

        # Determine retention policy
        should_retain = False
        if video_mode == "on":
            should_retain = True
        elif video_mode == "retain-on-failure" and status.lower() == "failed":
            should_retain = True

        all_pages = pages if pages else ([page] if page else [])
        raw_paths: List[Path] = []
        for p in all_pages:
            try:
                if p and p.video:
                    v_path = Path(p.video.path())
                    if v_path.exists() and v_path not in raw_paths:
                        raw_paths.append(v_path)
            except Exception as e:
                logger.debug(f"Could not retrieve video path for page: {e}")

        if not raw_paths:
            return None

        if not should_retain:
            # Video is not retained according to policy; delete if exists
            for raw_path in raw_paths:
                if raw_path.exists():
                    try:
                        raw_path.unlink()
                    except Exception as e:
                        logger.debug(f"Unable to delete unneeded video {raw_path}: {e}")
            return None

        # Target directory based on outcome
        if status.lower() == "passed":
            target_dir = PASSED_VIDEOS_DIR
        elif status.lower() == "skipped":
            target_dir = SKIPPED_VIDEOS_DIR
        else:
            target_dir = FAILED_VIDEOS_DIR
        CommonHelper.ensure_directory(target_dir)

        # Extract Test Case ID if present (e.g., E2E-HOME-001, E2E-ORDER_Purchase-001, E2E-Different_PDP-001)
        import re
        diff_pdp_match = re.search(r"E2E[-_]DIFFERENT[-_]PDP[-_](\d+)", test_name, re.IGNORECASE)
        order_tc_match = re.search(r"E2E[-_]ORDER[-_]PURCHASE[-_](\d+)", test_name, re.IGNORECASE)
        tc_match = re.search(r"(E2E[-_][A-Za-z0-9]+[-_]\d+)", test_name, re.IGNORECASE)
        if diff_pdp_match:
            tc_id = f"E2E-Different_PDP-{diff_pdp_match.group(1)}"
            target_file_name = f"{tc_id}_{status.lower()}.webm"
        elif order_tc_match:
            tc_id = f"E2E-ORDER_Purchase-{order_tc_match.group(1)}"
            target_file_name = f"{tc_id}_{status.lower()}.webm"
        elif tc_match:
            tc_id = tc_match.group(1).upper().replace("_", "-")
            target_file_name = f"{tc_id}_{status.lower()}.webm"
        else:
            clean_name = CommonHelper.sanitize_filename(test_name)
            timestamp = CommonHelper.get_timestamp()
            target_file_name = f"{clean_name}_{status.lower()}_{timestamp}.webm"

        target_path = target_dir / target_file_name

        try:
            # Case 1: Single page test (standard flow)
            if len(raw_paths) == 1:
                raw_video_path = raw_paths[0]
                try:
                    if page and page.video and raw_video_path == Path(page.video.path()):
                        page.video.save_as(str(target_path))
                    else:
                        shutil.move(str(raw_video_path), str(target_path))
                except Exception:
                    if raw_video_path.exists():
                        shutil.move(str(raw_video_path), str(target_path))

                logger.info(f"Saved {status} video for '{test_name}' at: {target_path}")
                return target_path

            # Case 2: Multi-page test (e.g., popup / new tab flow)
            logger.info(f"Merging {len(raw_paths)} page videos for '{test_name}'...")
            inputs = []
            filter_inputs = []
            for i, r_path in enumerate(raw_paths):
                inputs.extend(["-i", str(r_path)])
                filter_inputs.append(f"[{i}:v]scale=1280:720,setsar=1[v{i}]")

            concat_str = "".join([f"[v{i}]" for i in range(len(raw_paths))])
            filter_complex = ";".join(filter_inputs) + f";{concat_str}concat=n={len(raw_paths)}:v=1:a=0[outv]"

            cmd = [
                "ffmpeg", "-y",
                *inputs,
                "-filter_complex", filter_complex,
                "-map", "[outv]",
                "-c:v", "libvpx",
                "-deadline", "realtime",
                "-cpu-used", "8",
                "-b:v", "1M",
                str(target_path),
            ]

            merged = False
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if res.returncode == 0 and target_path.exists() and target_path.stat().st_size > 0:
                    merged = True
                    logger.info(f"Successfully merged {len(raw_paths)} videos for '{test_name}' at: {target_path}")
                    for r_path in raw_paths:
                        try:
                            r_path.unlink()
                        except Exception:
                            pass
                else:
                    logger.warning(f"ffmpeg merge non-zero exit ({res.returncode}): {res.stderr}")
            except Exception as e:
                logger.warning(f"ffmpeg video merge failed: {e}")

            if not merged:
                # Fallback: preserve the final destination page video
                dest_video = raw_paths[-1]
                shutil.move(str(dest_video), str(target_path))
                logger.info(f"Saved destination page fallback {status} video for '{test_name}' at: {target_path}")

            return target_path

        except Exception as e:
            logger.error(f"Error handling video for test '{test_name}': {e}")
            return None
