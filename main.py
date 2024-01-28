from selenium import webdriver
from selenium.common import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.by import By
import datetime
import pytz
import pause
from dateutil.relativedelta import relativedelta

# Sector 1-8 (1pm)
onePMtimes = []
# Sector 1-8 (2pm)
twoPMtimes = []
# Sector 1-8 (3pm)
threePMtimes = []


def initialise_weekly_time_list():
    sectors = 8
    today = datetime.date.today()

    # Calculate the upcoming Saturday and change type to string
    upcoming_saturday = today + relativedelta(weekday=5)

    # In yyyy/mm/dd format
    yyyymmdd = upcoming_saturday.strftime("%Y/%#m/%#d")
    # In date format ex. Fri 26 Jan
    dateformat = upcoming_saturday.strftime("%a %d %b")

    for sector in range(sectors):
        sector += 1
        onePMtimes.append(
            f"Date={yyyymmdd} Time=13:00 Availability= AvailablePRUEBA={dateformat} Court=Sector {sector}")
        twoPMtimes.append(
            f"Date={yyyymmdd} Time=14:00 Availability= AvailablePRUEBA={dateformat} Court=Sector {sector}")
        threePMtimes.append(
            f"Date={yyyymmdd} Time=15:00 Availability= AvailablePRUEBA={dateformat} Court=Sector {sector}")


def wait_midnight():
    # Get London time
    now = datetime.datetime.now(pytz.timezone('Europe/London'))

    # Time remaining until midnight
    tomorrow = now + datetime.timedelta(days=1)
    midnight = datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
    pause.until(midnight)


def badminton():
    # Wait until midnight
    wait_midnight()

    # Maybe add sleep for one second?

    # Configure the Selenium WebDriver
    driver = webdriver.Chrome()
    driver.set_window_size(2560, 1440)

    # Open the booking page
    driver.get("https://connect.activenewham.org.uk/Connect/memberHomePage.aspx")

    # Log in to the website
    username = driver.find_element(By.ID, "ctl00_MainContent_InputLogin")
    password = driver.find_element(By.ID, "ctl00_MainContent_InputPassword")

    # Populate form
    username.send_keys("")
    password.send_keys("")

    # Click login
    driver.find_element(By.ID, "ctl00_MainContent_btnLogin").click()

    # Click QuickBook
    driver.find_element(By.ID, "ctl00_MainContent_MostRecentBookings1_Bookings_ctl01_bookingLink").click()

    # Refresh page to ensure that Saturday is in last column
    driver.refresh()

    # Look to 7th column and choose options 1pm, 2pm, 3pm
    # Arbitrary number used in DOM to reference specified date and time (90 currently stands as 12pm hence += 7)
    elementnumber = 90
    while True:
        try:
            # Element number + 7 to push to next hour
            elementnumber += 7
            driver.find_element(By.ID, f"ctl00_MainContent_cal_calbtn{str(elementnumber)}").click()
            break
        except ElementClickInterceptedException:
            # Handle the case when the button is not found
            print("Button not found. Handle the error as needed.")

    # Searches substring within element only in Sector 1-8
    sector = -1  # This sector is out of bound. Same idea as while loop above
    alltimes = onePMtimes + twoPMtimes + threePMtimes
    while True:
        try:
            sector += 1  # Sector 1
            driver.find_element(By.CSS_SELECTOR, f'[data-qa-id*="{alltimes[sector]}"]').click()
            break
        except NoSuchElementException:
            # Handle the case when the button is not found
            print("No such element found. Handle the error as needed.")

    # Click Book
    driver.find_element(By.ID, "ctl00_MainContent_btnBasket").click()

    driver.quit()


if __name__ == '__main__':
    initialise_weekly_time_list()
    badminton()
