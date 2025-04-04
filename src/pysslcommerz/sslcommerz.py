import hashlib

import requests


class SSLCOMMERZ(object):
    store_id = None
    store_pass = None
    issandbox = None
    mode = None
    createSessionUrl = None
    validation_url = None
    transaction_url = None

    def __init__(self, config):
        self.store_id = config["store_id"]
        self.store_pass = config["store_pass"]
        self.mode = "sandbox" if (config["issandbox"]) else "securepay"
        self.createSessionUrl = (
            "https://" + self.mode + ".sslcommerz.com/gwprocess/v4/api.php"
        )
        self.validation_url = (
            "https://"
            + self.mode
            + ".sslcommerz.com/validator/api/validationserverAPI.php"
        )
        self.transaction_url = (
            "https://"
            + self.mode
            + ".sslcommerz.com/validator/api/merchantTransIDvalidationAPI.php"
        )

    def createSession(self, post_body: dict[str, str]):
        """
        Some mandatory parameters need to pass to SSLCommerz. It identify your customers and orders. Also you have to pass the success, fail, cancel url to redirect your customer after pay.
        Please follow this link https://developer.sslcommerz.com/.
        And Pass value with post_body

        """
        post_body["store_id"] = self.store_id
        post_body["store_passwd"] = self.store_pass
        return self.call_api("POST", self.createSessionUrl, post_body)

    def validationTransactionOrder(self, validation_id: str):
        """
        validation_id	: (mandatory) A Validation ID against the successful transaction which is provided by SSLCommerz.

        """
        params = {
            "val_id": validation_id,
            "store_id": self.store_id,
            "store_passwd": self.store_pass,
            "format": "json",
        }
        return self.call_api("GET", self.validation_url, params)

    def init_refund(self, bank_tran_id: str, refund_amount: str, refund_remarks: str):
        """
        bank_tran_id: (mandatory) The transaction ID at Banks End
        refund_amount: (mandatory) The amount will be refunded to card holder's account.
        refund_remarks: (mandatory)The reason of refund.
        """
        params = {
            "bank_tran_id": bank_tran_id,
            "refund_amount": refund_amount,
            "refund_remarks": refund_remarks,
            "store_id": self.store_id,
            "store_passwd": self.store_pass,
            "format": "json",
        }
        return self.call_api("GET", self.transaction_url, params)

    def query_refund_status(self, refund_ref_id: str):
        """
        refund_ref_id: (mandatory) This parameter will be returned only when the request successfully initiates
        """
        params = {
            "refund_ref_id": refund_ref_id,
            "store_id": self.store_id,
            "store_passwd": self.store_pass,
            "format": "json",
        }
        return self.call_api("GET", self.transaction_url, params)

    def transaction_query_session(self, sessionkey: str):
        """
        sessionkey: The session id (mandatory) has been generated at the time of transaction initiated.
        """

        params = {
            "sessionkey": sessionkey,
            "store_id": self.store_id,
            "store_passwd": self.store_pass,
            "format": "json",
        }
        return self.call_api("GET", self.transaction_url, params)

    def transaction_query_tranid(self, tran_id: str):
        """

        tran_id: Transaction ID (mandatory)  that was sent by you during initiation.

        """
        params = {
            "tran_id": tran_id,
            "store_id": self.store_id,
            "store_passwd": self.store_pass,
            "format": "json",
        }
        return self.call_api("GET", self.transaction_url, params)

    def hash_validate_ipn(self, post_body: dict[str, str]):
        """
        As IPN URL already set in panel. All the payment notification will reach through IPN prior to user return back. So it needs validation for amount and transaction properly.

        The IPN will send a POST REQUEST params that describes in 'https://developer.sslcommerz.com/'. Grab the post notification.

        """
        if self.checkKey(post_body, "verify_key") & self.checkKey(
            post_body, "verify_sign"
        ):
            verifyKeys = post_body["verify_key"].split(",")
            new_params = {}

            for key in verifyKeys:
                new_params[key] = post_body[key]

            storePass = self.store_pass.encode()

            hashingStorePass = hashlib.md5(storePass).hexdigest()

            new_params["store_passwd"] = hashingStorePass

            new_params = self.ksort(new_params)
            hashString = ""
            for key in new_params:
                hashString += key[0] + "=" + str(key[1]) + "&"

            hash_string = hashString.strip("&")
            hash_string_md5 = hashlib.md5(hash_string.encode()).hexdigest()
            if hash_string_md5 == post_body["verify_sign"]:
                return True
            else:
                return False
        else:
            return False

    def checkKey(self, post_body: dict[str, str], key: str):
        if key in post_body.keys():
            return True
        else:
            return False

    def ksort(self, d):
        return [(k, d[k]) for k in sorted(d.keys())]

    def call_api(self, method: str, url: str, payload: dict[str, str]):
        """
        Call the API with the given method, url, and payload.
        :param method: The HTTP method to use (GET, POST, PUT, DELETE).
        :param url: The URL to call.
        :param
        :param payload: The payload to send with the request.
        :return: The response from the API.
        """
        try:
            if method == "POST":
                response = requests.post(url, data=payload)

            elif method == "delete":
                response = requests.delete(url)

            elif method == "put":
                response = requests.put(url, data=payload)

            elif method == "GET":
                response = requests.get(url, params=payload)

            else:
                response = {"response": "Method is not valid"}
            return response.json()
        except Exception as e:
            print(e)
            # print("An exception occurred")
