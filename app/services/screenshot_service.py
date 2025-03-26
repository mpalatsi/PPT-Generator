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
import asyncio

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
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self) -> None:
        """Set up the Chrome WebDriver with appropriate options."""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            
            # Initialize ChromeDriver with automatic version detection
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            raise

    async def take_screenshot(self, url: str, output_path: str) -> str:
        """
        Take a screenshot of a webpage.
        
        Args:
            url: The URL to screenshot
            output_path: Where to save the screenshot
            
        Returns:
            The path to the saved screenshot
        """
        try:
            logger.info(f"Taking screenshot of {url}")
            self.driver.get(url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            await asyncio.sleep(2)
            
            # Take screenshot
            self.driver.save_screenshot(output_path)
            logger.info(f"Screenshot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            raise
    
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
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing Chrome WebDriver: {str(e)}")
    
    def __del__(self):
        """Clean up the WebDriver when the service is destroyed."""
        self.cleanup() 