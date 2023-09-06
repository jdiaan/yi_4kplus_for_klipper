# 如何使用Moonraker API
[官方手册](https://moonraker.readthedocs.io/en/latest/web_api/)
* 使用HTTP接口
* 使用JSON-RPC（自己研究，应该不难吧，我不会）
  
## 使用HTTP接口
情景介绍，我想通过我的电脑获取上位机的信息。当然你也可以在上位机里面自己查询自己的接口，一个道理。
1. 如果是其它电脑你需要知道上位机IP，我假设一个IP地址`192.168.1.10`。上位机自己查询应该用`locahost`或`127.0.0.1`之类的应该就行了吧，我没试过，不知道也不晓得
2. 比方说我想查找当前打印的文件。
   1. 直接在浏览器中输入`192.168.1.10/printer/objects/query?print_stats=filename`就可以啦
      * 🌟记得把IP设为你自己的！！！！
   2. 使用python的 `requests`库
        ```python
        import requests

        url = "http://192.168.1.10/printer/objects/query"  # 修改成你自己的ip
        myParams = {"print_stats": "filename"}  # 问号后的查询内容用字典代替

        res = requests.get(url=url, params=myParams)

        re_json = res.json()  # 就获取到你的json代码了

        ```
3. 返回了一串json代码，里面就包含了你的文件信息。简单吧
    ```json
    {
        "result": {
            "eventtime": 29645.060955301,
            "status": {
                "print_stats": {
                    "filename": "mflink_90_support_PETG_35m17s.gcode"
                }
            }
        }
    }
    ```


## 如何知道能查询哪些东西呢
看[官方手册](https://moonraker.readthedocs.io/en/latest/web_api/#printer-status)都有自己找

## 最后：
好了你又可以造自己的原子弹了