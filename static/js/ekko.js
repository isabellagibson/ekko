this.setCookie = (name, value, days) => {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
        expires = "; expires=" + date.toUTCString();
    }
    let newCookie = `${name}=${value || ""}${expires}; path=/`;
    document.cookie = newCookie;
    return newCookie;
};
this.getCookie = (cookieName) => {
    return ("; " + document.cookie).split(`; ${cookieName}=`).pop().split(";")[0];
};

function APIClient() {
    this.baseURL = `${window.location.origin}`;
    this.access_token = null;
    if (getCookie("org_data") !== "") {
        this.org_id = JSON.parse(atob(getCookie("org_data"))).id || null;
    } else {
        this.org_id = null;
    }
    this.getItem = async (item_type, item_id) => {
        return fetch(`${this.baseURL}/${item_type}/${item_id}`)
            .then((tmp) => tmp.json())
            .then((response) => {
                return response;
            });
    };
    if (getCookie("user_data") != "") {
        this.access_token = JSON.parse(atob(getCookie("user_data"))).api_key;
        this.headers = {
            Authorization: this.access_token
        };
    }
    this.login = async (org_id, username, password) => {
        return fetch(`${this.baseURL}/login`, {
            headers: {
                "Content-Type": "application/json",
            },
            method: "POST",
            body: JSON.stringify(
                {
                    'org_id': org_id,
                    'login_data': {
                        'username': username,
                        'password': password
                    }
                }),
        })
            .then((tmp) => tmp.json())
            .then((response) => {
                return response;
            });
    };
    this.deleteRecord = async (record_type, record_id) => {
        return fetch(`${this.baseURL}/${record_type}/${record_id}`, {
            headers: {
                Authorization: this.access_token,
            },
            method: "DELETE",
        })
            .then((tmp) => tmp.json())
            .then((response) => {
                return response;
            });
    };
    this.getUsers = async () => {
        return fetch(`${this.baseURL}/users`, {
            headers: {
                Authorization: this.access_token,
            },
            method: "GET",
        })
            .then((tmp) => tmp.json())
            .then((response) => {
                return response;
            });
    };
    this.createUser = async (data) => {
        return fetch(`${this.baseURL}/users`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: this.access_token,
            },
            body: JSON.stringify(data),
        })
            .then((tmp) => tmp.json())
            .then((response) => {
                return response;
            });
    };
    this.togglePlay = async (enabled) => {
        return fetch(
            `${this.baseURL}/orgs/${this.org_id}/play_enabled/${enabled}`,
            {
                method: "PUT",
                headers: {
                    Authorization: this.access_token,
                },
            }
        )
            .then((tmp) => tmp.json())
            .then((response) => {
                return response;
            });
    };
    this.getMD5 = async (x) => {
        return fetch(`${this.baseURL}/md5/${x}`, {
            method: 'GET',
        }).then((tmp) => tmp.json())
            .then((response) => {
                return response.md5;
            });
    }
    this.updateUser = async (data) => {
        return fetch(`${this.baseURL}/users/${data.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: this.access_token,
            },
            body: JSON.stringify(data),
        })
            .then((tmp) => tmp.json())
            .then((response) => {
                return response;
            });
    };
    this.getRecord = async (record_type, record_id) => {
        return fetch(`${this.baseURL}/${record_type}/${record_id}`, {
            method: "GET",
            headers: {
                Authorization: this.access_token,
            },
        })
            .then((tmp) => tmp.json())
            .then((response) => {
                return response;
            });
    };
    this.updateRecord = async (record_id, key, value) => {
        return fetch(`${this.baseURL}/${record_id}/${key}/${value}`, {
            method: "PUT",
            headers: {
                Authorization: this.access_token,
            },
        })
            .then((tmp) => tmp.json())
            .then((response) => {
                return response;
            });
    };
    this.getGroups = async () => {
        return fetch(`${this.baseURL}/groups`, {
            method: "GET",
            headers: {
                Authorization: this.access_token,
            },
        })
            .then((tmp) => tmp.json())
            .then((response) => {
                return response;
            });
    };
    this.updateOrg = async (postData) => {
        return fetch(`${this.baseURL}/orgs/${postData.id}`, {
            method: 'PUT',
            headers: {
                "Content-Type": "application/json",
                Authorization: this.access_token
            },
            body: JSON.stringify(postData)
        }).then((tmp) => tmp.json()).then((response) => {
            return response;
        })
    }
    this.sendPasswordReset = async (email) => {
        return fetch(`${this.baseURL}/send_password_reset`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ 'email': email })
        }).then((tmp) => tmp.json()).then((response) => {
            return response;
        })
    }
    this.resetPassword = async (token, password) => {
        return fetch(`${this.baseURL}/password_reset`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ 'token': token, 'password': password })
        }).then((tmp) => tmp.json()).then((response) => {
            return response;
        });
    }
    this.updateOwnPassword = async (newPassword) => {
        return fetch(`${this.baseURL}/change_password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'password': newPassword })
        }).then((tmp) => tmp.json()).then((response) => {
            return response;
        })
    }
}

const ekko = new APIClient();  