# achievement_system.py

class Achievement:
    def __init__(self, achievement_id, title, description, condition_func, icon_path=None):
        self.id = achievement_id
        self.title = title
        self.description = description
        self.condition_func = condition_func
        self.icon_path = icon_path

    def is_unlocked(self, user_data):
        """Return True if the user meets the achievement condition."""
        return self.condition_func(user_data)


class AchievementSystem:
    def __init__(self):
        self.global_achievements = {}
        self.load_achievements()

    def load_achievements(self):
        """Initialize the global set of achievements."""
        # Achievement: Earn your first 100 points
        self.global_achievements['first_100'] = Achievement(
            achievement_id='first_100',
            title='First 100 Earned!',
            description='Congratulations on earning your first 100 points!',
            condition_func=lambda user: user.balance >= 100,
            icon_path='frontend/assets/images/first_100.png'
        )
        # Add more achievements here as needed
        # self.global_achievements['another_id'] = Achievement(...)

    def check_achievements(self, user_data):
        """
        Check all achievements against the user data.
        If a user qualifies for an achievement they haven't already earned,
        record it and return the newly unlocked achievements.
        """
        newly_unlocked = []
        for achievement in self.global_achievements.values():
            if achievement.is_unlocked(user_data) and achievement.id not in user_data.achievements:
                user_data.achievements.append(achievement.id)
                newly_unlocked.append(achievement)
        return newly_unlocked

achievement_sys = AchievementSystem()