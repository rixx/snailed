from defusedxml.ElementTree import parse


def get_etree(fileish):
    return parse(fileish).getroot()


def to_datetime(value):
    # TODO
    return value


def to_delta(element):
    if not element:
        return
    return element.text


class Attempt:
    def __init__(self, number):
        """ Use the from_lss or the from_splits classmethods instead of the constructor. """
        self.number = number
        self.start_datetime = None
        self.end_datetime = None
        self.finished = None
        self.real_time = None
        self.game_time = None
        self.times = []

    @classmethod
    def from_lss(cls, element):
        attempt = Attempt(element.attrib["id"])
        attempt.start_datetime = to_datetime(element.attrib.get("started"))
        attempt.end_datetime = to_datetime(element.attrib.get("ended"))
        real_time = element.find("RealTime")
        if real_time:
            attempt.finished = True
            attempt.real_time = to_delta(element.find("RealTime"))
            attempt.game_time = to_delta(element.find("GameTime"))
        return attempt


class Segment:
    def __init__(self, name, icon=None):
        self.name = name
        self.icon = icon
        self.best_real_time = None
        self.best_game_time = None
        self.pb_real_time = None
        self.pb_game_time = None
        self.attempts = []


class SegmentTime:
    def __init__(self, real_time, game_time, segment, attempt):
        self.real_time = real_time
        self.game_time = game_time
        self.segment = segment
        self.attempt = attempt


class History:
    def __init__(self, game, category=None, patch=None):
        """ Use the from_lss or the from_splits classmethods instead of the constructor. """
        self.game = game
        self.category = category
        self.patch = patch
        self.other_metadata = {}
        self.attemts = {}

    @classmethod
    def from_lss(cls, root):
        history = cls(
            game=root.find("GameName").text,
            category=root.find("CategoryName").text,
            patch=root.find('Metadata/Variables/Variable[@name="Patch"]').text,
        )
        history.other_metadata = {  # Data that I don't know how to use
            "offset": root.find("Offset").text,
            "version": root.attrib.get("version"),
            "source": "LiveSplit",
        }

        history.attempts = {
            attempt.attrib.get("id"): Attempt.from_lss(attempt)
            for attempt in root.find("AttemptHistory")
        }
        history.segments = []
        for seg in root.find("Segments"):
            segment = Segment(seg.find("Name").text, icon=seg.find("Icon").text)
            segment.best_real_time = to_delta(seg.find("BestSegmentTime/RealTime"))
            segment.best_game_time = to_delta(seg.find("BestSegmentTime/GameTime"))
            pb = seg.find('SplitTimes/SplitTime[@name="Personal Best"]')
            if pb:
                segment.pb_real_time = to_delta(pb.find("RealTime"))
                segment.pb_game_time = to_delta(pb.find("GameTime"))

            for segment_time in seg.find("SegmentHistory"):
                real_time = to_delta(segment_time.find("RealTime"))
                game_time = to_delta(segment_time.find("GameTime"))
                attempt = history.attempts.get(segment_time.attrib.get("id"))
                time = SegmentTime(
                    segment=segment,
                    attempt=attempt,
                    real_time=real_time,
                    game_time=game_time,
                )
                segment.attempts.append(time)
                if attempt:
                    attempt.times.append(time)
                else:
        return history


def parse_lss_data(fileish):
    return History.from_lss(parse(fileish).getroot())
