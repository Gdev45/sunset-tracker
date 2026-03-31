import requests
from datetime import datetime, timedelta, timezone
from colorama import Fore, Style, init
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

init(autoreset=True)


def banner():
    print(Fore.RED + "=" * 50)
    print(Fore.YELLOW + "        🌅 SUN TIME CALCULATOR 🌇")
    print(Fore.RED + "=" * 50)


def get_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
    headers = {"User-Agent": "sunset-tracker-app"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            print(Fore.RED + f"❌ Error fetching location (HTTP {response.status_code})")
            return None, None

        data = response.json()
        if not data:
            print(Fore.RED + "❌ City not found.")
            return None, None

        return data[0]["lat"], data[0]["lon"]

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"❌ Network error: {e}")
        return None, None


def get_sun_times(lat, lon):
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(Fore.RED + f"❌ Error fetching sun data (HTTP {response.status_code})")
            return None, None, None

        data = response.json()["results"]

        # Determine timezone based on coordinates
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lat=float(lat), lng=float(lon))
        if not tz_name:
            print(Fore.RED + "❌ Could not determine timezone for location.")
            return None, None, None

        tz = ZoneInfo(tz_name)

        # Parse UTC times and convert to location timezone
        sunrise_utc = datetime.fromisoformat(data["sunrise"]).replace(tzinfo=timezone.utc)
        sunset_utc = datetime.fromisoformat(data["sunset"]).replace(tzinfo=timezone.utc)

        sunrise_local = sunrise_utc.astimezone(tz)
        sunset_local = sunset_utc.astimezone(tz)

        return sunrise_local, sunset_local, tz_name

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"❌ Network error: {e}")
        return None, None, None
    except Exception as e:
        print(Fore.RED + f"❌ Error parsing sun data: {e}")
        return None, None, None


def calculate_hours(sunrise, sunset):
    return {
        "morning_golden": (sunrise, sunrise + timedelta(hours=1)),
        "evening_golden": (sunset - timedelta(hours=1), sunset),
        "morning_blue": (sunrise - timedelta(minutes=30), sunrise),
        "evening_blue": (sunset, sunset + timedelta(minutes=30)),
    }


def format_time(t):
    offset = t.strftime("%z")
    offset_formatted = f"UTC{offset[:3]}:{offset[3:]}"
    return f"{t.strftime('%H:%M')} ({t.strftime('%Z')}, {offset_formatted})"


def main():
    banner()

    print(Fore.RED + "\nHow would you like to enter your location?")
    print("1) City name")
    print("2) Coordinates")

    choice = input(Fore.RED + "\nEnter choice (1/2): ").strip()

    if choice == "1":
        city = input(Fore.RED + "Enter city name: ")
        lat, lon = get_coordinates(city)
        if not lat:
            return
    elif choice == "2":
        print(Fore.RED + "\nEnter your coordinates:")
        lat = input("Latitude  : ")
        lon = input("Longitude : ")
    else:
        print(Fore.RED + "❌ Invalid choice.")
        return

    print(Fore.MAGENTA + "\nFetching sun data...\n")

    sunrise, sunset, tz_name = get_sun_times(lat, lon)
    if not sunrise or not sunset:
        return

    hours = calculate_hours(sunrise, sunset)

    print(Fore.RED + "=" * 50)
    print(Fore.YELLOW + f"🌞 SUN TIMES for timezone: {tz_name}")
    print(Fore.RED + "=" * 50)

    print(f"{Fore.GREEN}Sunrise:{Style.RESET_ALL} {format_time(sunrise)}")
    print(f"{Fore.RED}Sunset :{Style.RESET_ALL} {format_time(sunset)}")

    print(Fore.YELLOW + "\n GOLDEN HOUR")
    print(f"Morning: {format_time(hours['morning_golden'][0])} - {format_time(hours['morning_golden'][1])}")
    print(f"Evening: {format_time(hours['evening_golden'][0])} - {format_time(hours['evening_golden'][1])}")

    print(Fore.CYAN + "\n BLUE HOUR")
    print(f"Morning: {format_time(hours['morning_blue'][0])} - {format_time(hours['morning_blue'][1])}")
    print(f"Evening: {format_time(hours['evening_blue'][0])} - {format_time(hours['evening_blue'][1])}")

    print(Fore.RED + "\n" + "=" * 50)
    print(Fore.YELLOW + "✅ Done!")


if __name__ == "__main__":
    main()