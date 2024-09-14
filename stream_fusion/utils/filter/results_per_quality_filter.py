from stream_fusion.utils.filter.base_filter import BaseFilter
from stream_fusion.logging_config import logger

#TODO: Check if this filter is still needed and RTN changes for it.
class ResultsPerQualityFilter(BaseFilter):
    def __init__(self, config):
        super().__init__(config)
        self.max_results_per_quality = int(self.config.get('resultsPerQuality', 5))

    def filter(self, data):
        filtered_items = []
        resolution_count = {}

        for item in data:
            resolution = getattr(item.parsed_data, 'resolution', "?.BZH.?")
            
            if resolution not in resolution_count:
                resolution_count[resolution] = 1
                filtered_items.append(item)
            elif resolution_count[resolution] < self.max_results_per_quality:
                resolution_count[resolution] += 1
                filtered_items.append(item)

        logger.info(f"ResultsPerQualityFilter: input {len(data)}, output {len(filtered_items)}")
        return filtered_items

    def can_filter(self):
        return self.max_results_per_quality > 0
