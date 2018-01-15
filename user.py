"""
in this module, I define a obj user, which record user's information.
"""


# coding:utf-8


class User:
    """
    obj
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.followers = -1
        self.watchers = -1
        self.nickname = ''
        self.avatar_path = ''
        self.avatar_url = ''
        self.des = ''
        self.is_pro = 0  # 0 代表没有认证 1 代表认证了

    def dump(self):
        """from insert a User object to database"""
        return (self.user_id, self.followers,
                self.watchers, self.nickname,
                self.avatar_path, self.avatar_url,
                self.des, self.is_pro)
