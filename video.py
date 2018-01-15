"""
we define a video object to record video information.
"""


# coding: utf-8


class Video:
    """
    obj
    """

    def __init__(self, video_id):
        self.video_id = video_id
        self.user_id = ''
        self.title = ''
        self.upload_time = ''  # timestamp
        self.avatar_path = ''
        self.avatar_url = ''
        self.des = ''

    def dump(self):
        """for insert a new video object to sqlite database."""
        return (self.video_id, self.user_id,
                self.title, self.upload_time,
                self.avatar_path, self.avatar_url,
                self.des)
