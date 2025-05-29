import random
import string
import threading
import queue
import datetime
import time

import requests
import ephem
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

ua = UserAgent()
password_queue = queue.Queue()


def get_country(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 3,
        "addressdetails": 1,
    }
    headers = {
        "User-Agent": ua.random,
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("COULD NOT FETCH COUNTRY TRY AGAIN")
        print("COULD NOT FETCH COUNTRY TRY AGAIN")
        print("COULD NOT FETCH COUNTRY TRY AGAIN")
        raise ValueError()

    data = response.json()
    return data.get("address", {}).get("country", "").lower()


def generate_password():
    while True:
        password = ""

        """
        Rule 1
        Your password must be at least 5 characters.
        """

        # It will be anyways

        """
        Rule 2
        Your password must include a number.
        """

        # password += str(random.randint(0, 9))
        password += str(9)  # optimization for rule 5

        """
        Rule 3
        Your password must include an uppercase letter.
        """

        # optimization for rule 9
        roman_numerals = ['I', 'V', 'X', 'L', 'C', 'D', 'M']

        uppercase_letters = [
            c for c in string.ascii_uppercase if c not in roman_numerals]
        password += random.choice(uppercase_letters)

        """
        Rule 4
        Your password must include a special character.
        """

        password += random.choice(string.punctuation)

        """
        Rule 5
        The digits in your password must add up to 25.
        """

        current_sum = sum(int(c) for c in password if c.isdigit())

        while current_sum < 25:
            next_digit = 9 if current_sum + 9 <= 25 else 25 - current_sum
            password += str(next_digit)
            current_sum += next_digit

        """
        Rule 6
        Your password must include a month of the year.
        """

        # import calendar
        # password += random.choice({i: calendar.month_name[i] for i in range(1, 13)}).lower()
        password += "may"

        """
        Rule 7
        Your password must include a roman numeral.
        """

        # Will be at rule 9 anyways

        """
        Rule 8
        Your password must include one of our sponsors:
        """

        # Currently: pepsi, starbucks, shell
        # optimization "starbucks" has more chars
        password += random.choice(["pepsi", "shell"])

        """
        Rule 9
        The roman numerals in your password should multiply to 35.
        """

        password += "XXXV"

        """
        Rule 10
        Your password must include this CAPTCHA:
        """

        """ Using Playwright instead

        def get_captcha_answer():
            #import requests
            #from bs4 import BeautifulSoup

            headers = {
                # requests.exceptions.HTTPError: 403 Client Error: Forbidden for url: https://neal.fun/password-game/
                "User-Agent": ua.random,
                "Sec-Fetch-Site": "none",
            }

            response = requests.get("https://neal.fun/password-game/", headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            print(soup.text)
            captcha_div = soup.find("div", class_="captcha-wrapper")
            if captcha_div:
                img = captcha_div.find("img", class_="captcha-img")
                if img and "src" in img.attrs:
                    src = img["src"]
                    name = src.split("/")[-1].split(".")[0]
                    return name
            return None
        """

        # password += get_captcha_answer()

        """
        Rule 11
        Your password must include today's Wordle answer.
        """

        today = datetime.date.today().isoformat()

        headers = {
            "User-Agent": ua.random,
            "Sec-GPC": "1",
        }

        response = requests.get(
            f"https://neal.fun/api/password-game/wordle?date={today}", headers=headers
        )
        try:
            password += response.json().get("answer", "")
        except:
            pass

        """
        Rule 12
        Your password must include a two letter symbol from the periodic table.
        """

        periodic_table = [
            # optimized for rule 12 (no roman_numerals)
            "Ti"  # TODO add all others too
        ]

        password += random.choice(periodic_table)

        """
        Rule 13
        Your password must include the current phase of the moon as an emoji.
        """

        moon = ephem.Moon()
        moon.compute(datetime.datetime.now(datetime.timezone.utc))
        phase = moon.phase

        def moon_phase_to_emoji(phase):
            if phase < 2:
                return "🌑"
            elif phase < 10:
                return "🌒"
            elif phase < 15:
                return "🌓"
            elif phase < 21:
                return "🌔"
            elif phase < 28:
                return "🌕"
            elif phase < 35:
                return "🌖"
            elif phase < 40:
                return "🌗"
            elif phase < 48:
                return "🌘"
            else:
                return "🌑"

        password += moon_phase_to_emoji(phase)

        """
        Rule 15
        Your password must include a leap year.
        """

        # Rule 5 does this already (Year 92)
        # but in case its being broken because of rule 10
        password += str(0)

        """
        Rule 16
        Your password must include the best move in algebraic chess notation.
        """

        # TODO: IMPLEMENT

        print(password)
        password_queue.put(password)

        # https://thepasswordgame.netlify.app


def run_playwright():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        page.goto("https://neal.fun/password-game/")

        try:
            consent_button = page.query_selector('button:has-text("Consent")')
            if consent_button:
                consent_button.click()
        except Exception:
            pass

        page.wait_for_timeout(1000)

        threading.Thread(target=generate_password, daemon=True).start()

        page.wait_for_selector('.tiptap.ProseMirror[contenteditable="true"]')
        password_input = page.query_selector(
            '.tiptap.ProseMirror[contenteditable="true"]'
        )

        country = None
        chess = None

        while True:
            password = password_queue.get()
            password_input.click()
            password_input.fill(password)
            time.sleep(1)

            """
            Rule 10
            Your password must include this CAPTCHA:
            """

            captcha = ""
            captcha_imgs = page.query_selector_all("img")

            for img in captcha_imgs:
                src = img.get_attribute("src")
                if src and "/password-game/captchas/" in src and src.endswith(".png"):
                    captcha = src.split("/")[-1].replace(".png", "")
                    break

            # sum_of_captcha = sum(int(d) for d in captcha if d.isdigit())

            password_input.fill(password + captcha)

            # NOW DOING IT AGAIN AS THIS MESSES MY NUMS UP
            # PLEASE OPTIMISE THIS THIS IS A MESS
            """
            Rule 5
            The digits in your password must add up to 25.
            """

            # recalculate the sum of digits after adding captcha
            total_digits = [int(c) for c in captcha if c.isdigit()]
            captcha_sum = sum(total_digits)

            # subtract captcha_sum from the last digit(s) of the password so total is still 25
            digits_in_password = [
                i for i, c in enumerate(password) if c.isdigit()]
            if digits_in_password:
                # remove digits from the end of the password until the sum fits
                remaining = captcha_sum
                password_list = list(password)
                digit_indices = [i for i, c in enumerate(
                    password_list) if c.isdigit()]
                while remaining > 0 and digit_indices:
                    idx = digit_indices[-1]
                    digit_val = int(password_list[idx])
                    if digit_val <= remaining:
                        # remove this digit completely
                        remaining -= digit_val
                        del password_list[idx]
                        digit_indices.pop()
                    else:
                        # reduce this digit to fit
                        password_list[idx] = str(digit_val - remaining)
                        remaining = 0
                password = ''.join(password_list)

            # now fill with the adjusted password + captcha
            password_input.fill(password + captcha)

            # check if the sum is 25
            total_sum = sum(int(c)
                            for c in (password + captcha) if c.isdigit())
            if total_sum != 25:
                print(f"Warning: Digits sum to {total_sum}, not 25!")

            """
            Rule 14
            Your password must include the name of this country.
            """

            time.sleep(3)
            print("NOW READING LATITUDE")
            print("NOW READING LATITUDE")
            print("NOW READING LATITUDE")

            iframe = page.query_selector("iframe.geo")
            src = iframe.get_attribute("src") if iframe else None

            lat, lon = None, None

            if src and "!1d" in src and "!2d" in src:
                try:
                    # extract latitude
                    lat_str = src.split("!1d")[1].split("!2d")[0]
                    lat = float(lat_str)
                    # extract longitude
                    lon_str = src.split("!2d")[1].split("!3f")[0]
                    lon = float(lon_str)
                except Exception as e:
                    print(f"Error parsing lat/lon: {e}")
                    lat, lon = None, None

            if not country:
                country = get_country(lat, lon)

            password_input.fill(password + captcha + country)

            time.sleep(5)
            print("READING CHESS")
            print("READING CHESS")
            print("READING CHESS")

            chess_imgs = page.query_selector_all("img")
            for img in chess_imgs:
                src = img.get_attribute("src")
                if src and "/password-game/chess/puzzle" in src and src.endswith(".svg"):
                    svg_url = src if src.startswith(
                        "http") else f"https://neal.fun{src}"
                    try:
                        svg_resp = requests.get(
                            svg_url, headers={"User-Agent": ua.random})
                        svg_resp.raise_for_status()
                        with open("puzzle.svg", "wb") as f:
                            # This is literally the FEN string not a svg
                            # f.write(svg_resp.content)
                            print(svg_resp.content)
                            print(svg_resp.content)
                            print(svg_resp.content)
                            print(svg_resp.content)
                            print(svg_resp.content)
                            print(svg_resp.content)
                        print(f"Downloaded chess puzzle SVG: {svg_url}")
                    except Exception as e:
                        print(f"Failed to download {svg_url}: {e}")

            password_input.fill(password + captcha + country + chess)

            command = input("Enter a password to fill or 'exit' to quit: ")

            if command.lower() == "exit":
                break

            password_input.fill(command)

        browser.close()


try:
    threading.Thread(target=generate_password, daemon=True).start()
    run_playwright()
except KeyboardInterrupt:
    pass
except ValueError:
    threading.Thread(target=generate_password, daemon=True).start()
    run_playwright()

# print(generate_password()) # not needed anymore, password is auto-generated
