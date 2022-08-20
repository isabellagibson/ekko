let uri;

openCreateModal = () => {
    $('#createModal').modal('show');
    document.querySelector('#itemCard').style.visibility = 'hidden';
    document.querySelector('#tagID').value = '';
    document.querySelector('#playlistURL').value = '';
}

parseURL = async () => {
    // Hide the card if there is no playlist URL
    if (document.querySelector('#playlistURL').value === '') {
        document.querySelector('#itemCard').style.visibility = 'hidden';
    }
    // Parse the URL and fetch the information
    const url = document.querySelector('#playlistURL').value.split('://')[1].split('?')[0];
    const item_type = url.split('.com/')[1].split('/')[0];
    const item_id = url.split(`${item_type}/`)[1];
    uri = 'spotify: ' + item_type + ':' + item_id;
    const result = await ekko.getItem(item_type, item_id);
    // Set card info
    let curImg = undefined;
    if (result.images.length === 1) {
        curImg = result.images[0].url;
    } else {
        let curLen = 0;
        result.images.forEach(element => {
            if (element.width > curLen) {
                curImg = element.url;
                curLen = element.width;
            }
        });
    }
    document.querySelector('#itemName').innerText = result.name;
    document.querySelector('#itemImg').src = curImg;
    switch (item_type) {
        case 'album':
            document.querySelector('#itemOwner').innerText = result.artists[0].name;
            break;
        case 'playlist':
            document.querySelector('#itemOwner').innerText = result.owner.display_name;
            break;
        default:
            break;
    }
    document.querySelector('#itemCard').style.visibility = 'visible';
};

addTag = async () => {
    if (document.querySelector('#playlistURL').value === '' || document.querySelector('#tagID').value === '') {
        $('#createModal').modal('hide');
        Swal.fire({
            allowOutsideClick: false,
            backdrop: true,
            icon: "error",
            title: "Uh oh!",
            html: "In order to continue, please double check that you have tapped a tag and have filled out the playlist URL.",
        }).then(() => {
            $('#createModal').modal('show');
        });
    } else {
        console.log('TODO: Add Tag');
    }
}

scanTag = async () => {
    x = fetch(`${this.baseURL}/read_tag`)
        .then((tmp) => tmp.json())
        .then((response) => {
            return response;
        });
    console.log(x);
    document.querySelector('#tagID').value = x.data;
}