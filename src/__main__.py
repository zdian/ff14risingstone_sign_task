import logging
from typing import Any

from . import settings
from .client import get_sign_reward, get_sign_reward_list, get_user_info, sign_in
from .models import SignRewardItemGetType
from .utils import get_current_month


def main():
    logging.info("开始签到")
    # 支持多个cookie，以换行分割
    cookies = settings.input_cookie.split("\n")
    for cookie in cookies:
        if cookie:
            sign_in(cookie)

            if settings.input_check_house_remain:
                logging.info("开始检查房屋拆除倒计时")
                user_info: dict[str, Any] = get_user_info(cookie)
                house_remain_day = (
                    user_info.get("data", {})
                    .get("characterDetail", [{}])[0]
                    .get("house_remain_day")
                )
                if house_remain_day:
                    raise Exception(f"房屋拆除倒计时：{house_remain_day}")

            if settings.input_get_sign_reward:
                reward_list = get_sign_reward_list(get_current_month(), cookie)
                logging.info(f"本月奖励列表：{reward_list}")
                for reward in filter(
                    lambda reward: reward.is_get == SignRewardItemGetType.AVAILABLE,
                    reward_list
                ):
                    logging.info(f"开始领取签到奖励：{reward.item_name}")
                    r = get_sign_reward(reward.id, get_current_month(), cookie)
                    logging.info(r.json())


if __name__ == "__main__":
    main()
