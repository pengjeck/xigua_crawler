"""
in this module, I define a obj change, which record the change infomation of a video in a timestamp.
"""


# coding:utf-8


class Tempor:
    """
    obj
    """

    def __init__(self, video_id, time, views, likes, dislikes, comments):
        self.video_id = video_id
        self.time = time
        self.views = views
        self.likes = likes
        self.dislikes = dislikes
        self.comments = comments

    def dump(self):
        """for insert a Change obj to database."""
        return self.video_id, self.time, self.views, self.likes, self.dislikes, self.comments
