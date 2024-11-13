from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str

    @property
    def GET_TOKEN(self):
        return self.BOT_TOKEN

    model_config = SettingsConfigDict(env_file="../config/bot.env")


settings = Settings()