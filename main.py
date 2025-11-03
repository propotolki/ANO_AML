import logging
from bot import VkBotFedor
import config


def main():
    logging.basicConfig(level=logging.INFO)
    bot = VkBotFedor(token=config.VK_TOKEN, group_id=config.GROUP_ID)
    bot.run()


if __name__ == "__main__":
    main()



