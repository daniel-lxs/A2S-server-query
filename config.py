import yaml


class Config:

    def __init__(self, path):
        self.path = path  # Store the path for later use
        self.servers = {}
        self.token = None
        self.timeout = 5
        self.player_count_channel_id = ""
        self.reload()  # Load the initial configuration from the file

    def reload(self):
        with open(self.path, 'r') as f:
            config_data = yaml.safe_load(f)

        for key, value in config_data.items():
            if key == 'servers':
                self.servers = value
            else:
                setattr(self, key, value)
