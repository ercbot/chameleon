from kani import Kani


class LogMessagesKani(Kani):
    def __init__(self, engine, log_filepath: str = None,  *args, **kwargs):
        super().__init__(engine, *args, **kwargs)
        self.log_filepath = log_filepath

    async def add_to_history(self, message, *args, **kwargs):
        await super().add_to_history(message, *args, **kwargs)

        # Logs Message to File
        if self.log_filepath:
            with open(self.log_filepath, "a") as log_file:
                log_file.write(message.model_dump_json())
                log_file.write("\n")