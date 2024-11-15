import uuid
import logging

import httpx

from . import settings
from .models import SealType, SignRewardListResponse

def make_client(cookie):
    client = httpx.Client(
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": settings.input_user_agent,
            "Cookie": cookie
        },
        timeout=30,
    )
    return client
    
# client = httpx.Client(
#     headers={
#         "Content-Type": "application/x-www-form-urlencoded",
#         "User-Agent": settings.input_user_agent,
#         "Cookie": settings.input_cookie
#     },
#     timeout=30,
#     # verify=False,
#     # proxies="http://127.0.0.1:8888",
# )

client_wx = httpx.Client(timeout=30)

def get_wecom_token():
    r = client_wx.get(
        f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={settings.input_corpid}&corpsecret={settings.input_secret}"
    )
    logging.info(r.json())
    return r.json().get("access_token")


def send_wecom(msg):
    if access_token := get_wecom_token():
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
        headers = {"Content-Type": "application/json"}
        data = {
            "touser": settings.input_touser,
            "agentid": settings.input_agentid,
            "msgtype": "text",
            "text": {"content": msg},
        }
        r = client_wx.post(url=url, headers=headers, json=data)
        logging.info(r.text)
    else:
        logging.info("没有获得token，发送企业微信消息失败")


def do_seal(type_: SealType, cookie):
    r = make_client(cookie).post(
        f"{settings.input_base_url}/api/home/active/online2312/doSeal",
        data={"type": type_},
    )

    logging.info(r.text)
    if (
        settings.input_corpid
        and settings.input_secret
        and settings.input_agentid
        and settings.input_touser
    ):
        send_wecom(r.text)


def is_login_in(cookie):
    r = make_client(cookie).get(
        f"{settings.input_base_url}/api/home/sysMsg/getSysMsg",
        params={
            "page": 1,
            "limit": 10,
            "tempsuid": str(uuid.uuid4()),
        },
    )

    logging.info(r.text)


def sign_in(cookie):
    r = make_client(cookie).post(
        f"{settings.input_base_url}/api/home/sign/signIn",
        params={
            "tempsuid": str(uuid.uuid4()),
        },
        data={
            "tempsuid": str(uuid.uuid4()),
        }
    )

    logging.info(r.text)
    send_wecom(r.text)


def like(cookie):
    r = make_client(cookie).post(
        f"{settings.input_base_url}/api/home/posts/like",
        params={
            "tempsuid": str(uuid.uuid4()),
        },
        data={"id": settings.input_like_post_id, "type": 1},
    )
    logging.info(r.text)

    return r


def comment(cookie):
    r = make_client(cookie).post(
        f"{settings.input_base_url}/api/home/posts/comment",
        params={
            "tempsuid": str(uuid.uuid4()),
        },
        data={
            "content": settings.input_comment_content,
            "posts_id": settings.input_comment_post_id,
            "parent_id": "0",
            "root_parent": "0",
            "comment_pic": "",
        },
    )

    logging.info(r.text)


def get_user_info(cookie):
    r = make_client(cookie).get(
        f"{settings.input_base_url}/api/home/userInfo/getUserInfo",
        params={"page": 1},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()

    return r


def get_sign_reward(id_, month, cookie):
    r = make_client(cookie).post(
        f"{settings.input_base_url}/api/home/sign/getSignReward",
        params={
            "tempsuid": str(uuid.uuid4()),
        },
        data={
            "id": id_,
            "month": month,
            "tempsuid": str(uuid.uuid4()),
        },
    )

    return r


def get_sign_reward_list(month, cookie):
    r = make_client(cookie).get(
        f"{settings.input_base_url}/api/home/sign/signRewardList",
        params={
            "month": month,
            "tempsuid": str(uuid.uuid4()),
        },
    )

    return SignRewardListResponse.model_validate_json(r.text).data
