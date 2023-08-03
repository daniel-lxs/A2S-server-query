import yaml

class Config:

    def __init__(self, path):
        self.servers = {}
        self.token = None
        self.timeout = 5
        self.player_count_channel_id = ""

        with open(path, 'r') as f:
            config_data = yaml.safe_load(f)

        for key, value in config_data.items():
            if key == 'servers':
                self.servers = value
            else:
                setattr(self, key, value)

