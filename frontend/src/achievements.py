import pygame
import pygame_gui
import requests
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, FONT, SERVER_URL, BLACK
from user_session import UserSession

# Global variables to store the popup button and achievement data.
achievement_popup_button = None
achievement_data = None
pending_achievements = []
current_achievement = None
new_achievements = []
show_achievement_popup = False

def set_ach_popup(bool):
    global show_achievement_popup
    show_achievement_popup = bool

def get_ach_popup():
    global show_achievement_popup
    return show_achievement_popup

ACHIEVEMENT_CONDITIONS = {
    "first_100": lambda user: float(user["net_worth"]) >= 100,
    # add more here, keyed by the same IDs returned by the backend
}

def check_achievements(user_id):
    BASE_URL = SERVER_URL

    # 1️⃣ Get the user’s profile (net_worth, username, etc.)
    profile_resp = requests.get(f"{BASE_URL}/profile/{user_id}")
    profile_resp.raise_for_status()
    user_data = profile_resp.json()
    print(user_data)

    # 2️⃣ Get already-earned achievement IDs
    earned_resp = requests.get(f"{BASE_URL}/achievements/{user_id}")
    earned_resp.raise_for_status()
    earned_ids = {ach["id"] for ach in earned_resp.json().get("achievements", [])}
    print(earned_ids)

    # 3️⃣ Evaluate each global achievement
    for ach_id, ach in GLOBAL_ACHIEVEMENTS.items():
        condition = ACHIEVEMENT_CONDITIONS[ach_id]
        if ach_id not in earned_ids and condition(user_data):
            new_achievements.append(ach)
    return new_achievements

def load_global_achievements():
    resp = requests.get(f"{SERVER_URL}/achievements/definitions")
    resp.raise_for_status()
    return {ach['id']: ach for ach in resp.json()['achievements']}

GLOBAL_ACHIEVEMENTS = load_global_achievements()

def get_achievement():
    session = UserSession()
    response = requests.get(f"{SERVER_URL}/achievements/{session.get_user()}")
    print("Response status:", response.status_code)
    print("Response text:", response.text)
    try:
        data = response.json()
    except Exception as e:
        print("Error decoding JSON:", e)
        return None
    
    if data.get("achievements") and len(data["achievements"]) > 0:
        return data["achievements"][0]
    else:
        return []

def initialize_achievement_popup(ui_manager):
    global pending_achievements, current_achievement, achievement_popup_button, new_achievements

    print("▶ initialize_achievement_popup called")
    print("   new_achievements:", new_achievements)

    pending_achievements = new_achievements.copy()
    if not pending_achievements:
        return

    current_achievement = pending_achievements.pop(0)
    print("   current_achievement set to:", current_achievement)

    ui_manager.clear_and_reset()

    icon_path = current_achievement.get("icon_path")
    if icon_path:
        try:
            icon_image = pygame.image.load(icon_path).convert_alpha()
            icon_image = pygame.transform.scale(icon_image, (64, 64))  # Resize to standard
            current_achievement["icon_image"] = icon_image
            print(f"   Icon loaded from: {icon_path}")
        except Exception as e:
            print(f"⚠️ Failed to load icon: {e}")
            current_achievement["icon_image"] = None
    else:
        current_achievement["icon_image"] = None
        print("   No icon_path provided")

    # Build the OK button
    text_surface = FONT.render(current_achievement["title"], True, WHITE)
    width, height = text_surface.get_width() + 40, text_surface.get_height() + 20
    x = SCREEN_WIDTH//2 - width//2
    y = SCREEN_HEIGHT*3//4

    print(f"   Creating button at ({x}, {y}) size ({width}, {height})")

    achievement_popup_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((x, y), (width, height)),
        text="OK",
        manager=ui_manager,
        object_id="#achievement"
    )
    print("   Achievement popup initialized\n")

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        test_line = f"{current} {word}".strip()
        if font.size(test_line)[0] <= max_width:
            current = test_line
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_achievement_popup(screen, events, ui_manager):
    global current_achievement

    if current_achievement is None:
        return
    print("▶ draw_achievement_popup — showing:", current_achievement["id"])

    screen.fill(BLACK)
    title = FONT.render(current_achievement["title"], True, WHITE)
    screen.blit(title, ((SCREEN_WIDTH-title.get_width())//2, 200))

    icon_image = current_achievement.get("icon_image")
    if icon_image:
        icon_x = (SCREEN_WIDTH - icon_image.get_width()) // 2
        icon_y = 200 - icon_image.get_height() - 10
        screen.blit(icon_image, (icon_x, icon_y))

    max_width = SCREEN_WIDTH - 100  # leave 50px margin each side
    wrapped_lines = wrap_text(current_achievement["description"], FONT, max_width)
    y=250
    for line in wrapped_lines:
        rendered = FONT.render(line, True, WHITE)
        screen.blit(rendered, ((SCREEN_WIDTH - rendered.get_width()) // 2, y))
        y += rendered.get_height() + 4


    for event in events:
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == achievement_popup_button:
            # Persist this achievement
            session = UserSession()
            user_id = session.get_user()
            ack_resp = requests.post(
                f"{SERVER_URL}/achievements/acknowledge",
                json={"user_id": user_id, "achievement_id": current_achievement["id"]}
            )
            if ack_resp.status_code == 200:
                print(f"✅ Achievement {current_achievement['id']} saved for user")
            else:
                print("⚠️ Failed to acknowledge achievement:", ack_resp.text)

            # Advance to the next popup (or clear if done)
            if pending_achievements:
                initialize_achievement_popup(ui_manager)
            else:
                current_achievement = None
                set_ach_popup(False)

    ui_manager.update(1/60)
    ui_manager.draw_ui(screen)
    pygame.display.flip()

