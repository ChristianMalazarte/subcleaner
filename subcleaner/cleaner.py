from .subtitle import Subtitle
from .sub_block import SubBlock
from re import findall, IGNORECASE
from datetime import timedelta


class Cleaner(object):

    purge_regex_list: list
    warning_regex_list: list

    def __init__(self):
        self.purge_regex_list = []
        self.warning_regex_list = []

    def run_regex(self, subtitle: Subtitle):
        blocks = subtitle.blocks
        for block in blocks:
            for regex in self.purge_regex_list:
                result = findall(regex, block.content.replace("\n", " "), flags=IGNORECASE)
                if result is not None and len(result) > 0:
                    block.regex_matches = 3
                    break

            for regex in self.warning_regex_list:
                result = findall(regex, block.content.replace("\n", " "), flags=IGNORECASE)
                if result is not None:
                    block.regex_matches += len(result)

        for index in range(len(subtitle.blocks)):
            for block in subtitle.blocks[max(index-10, index): min(index+10, len(subtitle.blocks))]:
                if block.regex_matches >= 3:
                    subtitle.blocks[index].regex_matches += 1
                    break

    @staticmethod
    def remove_ads(subtitle: Subtitle):
        for block in subtitle.ad_blocks:
            subtitle.remove_block(block)
        for index in range(len(subtitle.blocks) - 1):
            block: SubBlock = subtitle.blocks[index]
            block.index = index+1

    @staticmethod
    def find_ads(subtitle: Subtitle):
        for block in subtitle.blocks:
            block: SubBlock
            if block.regex_matches >= 3:
                subtitle.ad_blocks.append(block)
            elif block.regex_matches == 2:
                subtitle.warning_blocks.append(block)

    @staticmethod
    def fix_overlap(subtitle: Subtitle) -> None:
        if len(subtitle.blocks) < 2:
            return

        margin: timedelta = timedelta(seconds=0.0417)
        previous_block: SubBlock = subtitle.blocks[0]
        for block in subtitle.blocks[1:]:
            block: SubBlock
            stop_time: timedelta = previous_block.stop_time + margin
            start_time: timedelta = block.start_time - margin
            overlap: timedelta = stop_time - start_time
            if overlap.days >= 0 and overlap.microseconds > 3000:
                content_ratio = len(block.content) / (len(block.content) + len(previous_block.content))
                block.start_time += content_ratio * overlap
                previous_block.stop_time += (content_ratio-1) * overlap
            previous_block = block
        return
