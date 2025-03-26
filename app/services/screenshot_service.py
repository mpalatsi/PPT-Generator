"""
Service for capturing screenshots from URLs using Selenium.
"""
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from fastapi import HTTPException
import time
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class ScreenshotService:
    """Service for capturing screenshots from web pages."""
    
    def __init__(self, output_dir: str = "temp/screenshots"):
        """
        Initialize the screenshot service.
        
        Args:
            output_dir: Directory to save screenshots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._setup_driver()
    
    def _setup_driver(self) -> None:
        """Set up the Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            # Get the ChromeDriver path and ensure it's the executable
            driver_path = ChromeDriverManager().install()
            driver_dir = os.path.dirname(driver_path)
            driver_exe = os.path.join(driver_dir, "chromedriver.exe")
            
            if not os.path.exists(driver_exe):
                # If chromedriver.exe is not found, try to find it in the directory
                for file in os.listdir(driver_dir):
                    if file.lower().endswith("chromedriver.exe"):
                        driver_exe = os.path.join(driver_dir, file)
                        break
                else:
                    raise FileNotFoundError("ChromeDriver executable not found")
            
            service = Service(executable_path=driver_exe)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("ChromeDriver initialized successfully")
        except Exception as e:
            logger.error(f"Error setting up ChromeDriver: {str(e)}")
            raise

    async def take_screenshot(self, url: str, output_path: str) -> None:
        """
        Take a screenshot of a webpage.
        
        Args:
            url: The URL to capture
            output_path: Path where to save the screenshot
        """
        try:
            # Create a new driver instance for each screenshot
            self._setup_driver()
            
            # Navigate to URL
            logger.info(f"Navigating to URL: {url}")
            self.driver.get(url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Set viewport size
            self.driver.set_window_size(1920, 1080)
            
            # Wait for dynamic content
            time.sleep(2)
            
            # Take screenshot
            logger.info(f"Taking screenshot and saving to: {output_path}")
            self.driver.save_screenshot(output_path)
            
        except TimeoutException:
            logger.error(f"Timeout while loading page: {url}")
            raise HTTPException(status_code=500, detail="Failed to load webpage")
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to capture screenshot")
        finally:
            # Clean up
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error cleaning up driver: {str(e)}")
    
    def capture_screenshots(self, url: str, num_slides: int) -> List[str]:
        """
        Capture screenshots from the given URL.
        
        Args:
            url: The URL to capture screenshots from
            num_slides: Number of screenshots to capture
            
        Returns:
            List of paths to the captured screenshots
        """
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for initial page load
            
            # Wait for the body to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page height and calculate scroll steps
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_step = page_height / num_slides
            
            screenshots = []
            for i in range(num_slides):
                # Scroll to position
                scroll_position = int(scroll_step * i)
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
                time.sleep(0.5)  # Wait for scroll to complete
                
                # Capture screenshot
                screenshot_path = self.output_dir / f"screenshot_{i+1}.png"
                self.driver.save_screenshot(str(screenshot_path))
                screenshots.append(str(screenshot_path))
            
            return screenshots
            
        except TimeoutException:
            logger.error(f"Timeout while loading page: {url}")
            raise
        except Exception as e:
            logger.error(f"Error capturing screenshots: {str(e)}")
            raise
        finally:
            self.driver.quit()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.driver.quit()
        except Exception as e:
            logger.error(f"Error cleaning up driver: {str(e)}") 