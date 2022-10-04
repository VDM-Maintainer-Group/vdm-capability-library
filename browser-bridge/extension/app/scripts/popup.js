
let old_input = document.getElementById('original_password');
let new_input = document.getElementById('new_password');
let re_input  = document.getElementById('confirm_password');
let main_form = document.getElementById('main_form')

let old_hint = document.getElementById('old_hint')
let new_hint = document.getElementById('new_hint')
let re_hint = document.getElementById('re_hint')

function set_valid(obj, hint) {
    obj.setAttribute('aria-invalid', 'false')
    hint.style.display = 'none'
    return true
}

function set_invalid(obj, hint) {
    obj.setAttribute('aria-invalid', 'true')
    hint.style.display = 'block'
    return false
}

function clear_warning(obj, hint) {
    obj.removeAttribute('aria-invalid')
    hint.style.display = 'none'
    return false
}

function check_validity() {
    const regex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
    if (new_input.value.length===0) {
        return clear_warning(new_input, new_hint)
    }
    else {
        if (new_input.value.match(regex)) {
            return set_valid(new_input, new_hint);
        }
        else {
            return set_invalid(new_input, new_hint);
        }
    }
}

function check_consistency() {
    if (re_input.value.length===0) {
        return clear_warning(re_input, re_hint)
    }
    else {
        if (re_input.value === new_input.value) {
            return set_valid(re_input, re_hint)
        }
        else {
            return set_invalid(re_input, re_hint)
        }
    }
}

function SHA256(message, callback) {
    const msgUint8 = new TextEncoder().encode(message);
    crypto.subtle.digest('SHA-256', msgUint8)
    .then((hashBuffer) => {
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
        callback(hashHex)
    });
}

function _save_password() {
    SHA256(new_input.value, (digest_passwd) => {
        browser.storage.sync.set({'digest_passwd':digest_passwd})
        .then(() => {
            window.close()
        }, (err) => {
            console.error(err)
            alert('Internal Error: password not updated!')
            window.close()
        })
    });
}

function save_password(event) {
    event.preventDefault();

    browser.storage.sync.get('digest_passwd', (items) => {
        if (!(check_validity() && check_consistency())) {
            return;
        }

        if ('digest_passwd' in items) {
            SHA256(old_input.value, (hash) => {
                if (!(hash==items['digest_passwd'])) {
                    set_invalid(old_input, old_hint);
                }
                else {
                    _save_password();
                }
            });
        }
        else {
            _save_password();
        }
    });
}


// set `original_password` disability
window.addEventListener('pageshow', () => {
    browser.storage.sync.get('digest_passwd', (items) => {
        if ('digest_passwd' in items) {
            old_input.removeAttribute('disabled')
            old_input.setAttribute('required', '')
        }
        else {
            old_input.setAttribute('disabled', '')
            old_input.removeAttribute('required')
        }
    });
});
// set event handlers
old_input.addEventListener('input', () => clear_warning(old_input, old_hint));
new_input.addEventListener('input', check_validity);
re_input.addEventListener('input', check_consistency);
main_form.addEventListener('submit', save_password);
