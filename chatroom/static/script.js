$(document).ready(function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var current_room_id;
    var current_room_name;
    var current_room_owner_id;
    var current_user_id = $('#username').attr('data-user-id');
    var current_username = $('#username').text();

    $("#invite-input").on("keyup", function (e) {
        var value = $(this).val().toLowerCase();
        // $('#username-dropdown a:contains()')
        // $('.input-holder span').text()

        if (e.which == 8 && $(this).val() == '')
            $(this).prev().remove();
        // else if(e.which == 32 && $(this).val() == )

        $('.dropdown-menu a').filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });

        $('.input-holder span').each(function(){
            var username = $(this).text();
            $(".dropdown-menu a:contains('" + username + "')").toggle(false);
        });
    });


    $('.dropdown-menu').on('click', 'a', function (e) {
        e.preventDefault();
        var username = $(this).html();
        $(this).toggle(false);
        $('#invite-input').before('<span class="badge badge-secondary align-self-center mr-1">' + username + '</span>');
        $('input').val('');
        // $('#invite-input').load("#invite-input");
    });

    $('.modal').on('shown.bs.modal', function () {
        $(this).find('input').focus();

        if ($(this).attr('id') == 'invite-modal') {
            $('#username-dropdown').empty();
            get_not_in_room_users(current_room_id).then(users => {
                jQuery.each(users, function () {
                    $('#username-dropdown').append('<a class="dropdown-item" href="#">' + this.username + '</a>');
                });
            });
        }
    });

    $('.modal').on('hidden.bs.modal', function () {
        $('input').val('');
        if ($(this).attr('id') == 'invite-modal') {
            $('.dropdown').find('span').remove();
        }
    });

    $('div#room-list').on('click', 'a.room', function (e) {
        e.preventDefault();
        console.log($(this));
        let room_id = parseInt($(this).attr('href'));

        $('#room-list a.active').addClass('list-group-item-light').removeClass('active');
        $(this).addClass('active').removeClass('list-group-item-light');
        $('div.chat-box').empty();
        load_room(room_id);
        history.pushState('data to be passed', '', '/room/' + room_id);
    });

    socket.on('connect', function () {
        socket.emit('my event', {
            data: 'User Connected'
        });
    });

    $('#message-form').on('submit', function (e) {
        e.preventDefault();
        if (current_room_id) {
            let user_input = $('#message-input-box').val();
            if (user_input) {
                socket.emit('send', {
                    username: current_username,
                    user_id: current_user_id,
                    room_id: current_room_id,
                    message: user_input
                });
            }
        }
        $('#message-input-box').val('').focus();
    });

    $('#invite-form').on('submit', function (e) {
        e.preventDefault();
        var users = [];
        $(".input-holder span").each(function () { users.push($(this).text()); });
        $('#invite-modal').modal('hide');
        invite_room(current_room_id, users);
        update_member_list(current_room_id);
    });

    $('#create-form').on('submit',function (e) {
        console.log('create');
        e.preventDefault();
        let room_name = $('#create-room-input').val();
        create_room(room_name);
        $('#create-modal').modal('hide');
        socket.on('redirect room', function (room_id) {
            window.location.replace('http://' + document.domain + ':' + location.port + '/room/' + room_id);
        });
    });

    $('#confirm-delete').find('.btn-ok').click(function () {
        console.log('delet');
        $('#confirm-delete').modal('hide');
        $('#chatroom-title').text('');
        $('.room-modal').addClass('d-none');
        $('#room-list a.active').remove();
        $('div.chat-box').empty();
        delete_room(current_room_id);
        history.pushState('data to be passed', '', '');
    });

    // $('#confirm-delete').on('show.bs.modal', function () {
    //     $(this).find('.btn-ok').click(function () {
    //         console.log('delet');
    //         $('#confirm-delete').modal('hide');
    //         $('#chatroom-title').text('');
    //         $('.room-modal').addClass('d-none');
    //         $('#room-list a.active').remove();
    //         $('div.chat-box').empty();
    //         delete_room(current_room_id);
    //         history.pushState('data to be passed', '', '');
    //     });
    // });

    $('#join').click(function () {
        let room = $('#room').val();
        socket.emit('join', room);
        $('h2#roomname').text(room);
        $('#room').val('');
    });

    $("#leave").click(function () {
        socket.emit('leave');
    });

    socket.on('room info', function (rooms) {
        // $('div.message_holder').append('<div><b style="color: #000">' + msg + '</b></div>')
        console.log(rooms);
    });

    socket.on('message', function (msg) {
        if (current_room_id == msg.room_id) {
            if (current_user_id == msg.user_id)
                append_receiver_chat_box(msg.message, msg.datetime);
            else
                append_sender_chat_box(msg.message, msg.datetime, msg.username);
            scroll_bottom('chat-box');
        } else {
            $('#room-list .room[data-room-id=' + msg.room_id + '] i').removeClass('d-none');
        }
    });

    function init() {
        let room_id = -1;
        if (window.location.pathname.match(/^\/room\/[0-9]+$/g)) {
            room_id = window.location.pathname.split("/").slice(-1)[0];
            load_room(room_id);
        }
        load_room_list(room_id);
    }

    function load_room(room_id){
        $('.room-modal').removeClass('d-none');
        $('#room-list .room[data-room-id= ' + room_id + '] i').addClass('d-none'); // remove notification dot

        get_room(room_id).then(room => {
            current_room_id = room.id;
            current_room_name = room.name;
            current_room_owner_id = room.owner_id;

            room.users[0] = room.users[0] + ' (owner)';
            $('#chatroom-title').attr('title', 'Members:\r\n' + room.users.join('\r\n'));
            $('#chatroom-title').text(current_room_name);
            $('.current-room').text(current_room_name);
            update_delete_leave_button(current_user_id == current_room_owner_id);
            render_messages(room.messages);
            scroll_bottom('chat-box');
        });
    }

    function update_delete_leave_button(bool){
        if (bool){
            $('.delete-leave').text('Delete');
            $('i.fa-trash').removeClass('d-none');
            $('i.fa-sign-out').addClass('d-none');
        } else {
            $('.delete-leave').text('Leave');
            $('i.fa-trash').addClass('d-none');
            $('i.fa-sign-out').removeClass('d-none');
        }
    }

    function update_member_list(room_id){
        get_room_members(room_id).then(usernames => {
            usernames[0] = usernames[0] + ' (owner)';
            $('#chatroom-title').attr('title', 'Members:\r\n' + usernames.join('\r\n'));
        });

    }

    const get_room_list = async () => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/room_list');
        const room_list = await response.json();
        return room_list;
    };

    const get_room = async (room_id) => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/room/' + room_id + '/data');
        const messages = await response.json();
        return messages;
    };

    // const get_users = async () => {
    //     const response = await fetch('http://' + document.domain + ':' + location.port + '/users');
    //     const users = await response.json();
    //     return users;
    // }

    const get_not_in_room_users = async (room_id) => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/room/' + room_id + '/' + 'not_members');
        const users = await response.json();
        return users;
    };

    const get_room_members = async (room_id) => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/room/' + room_id + '/' + 'users');
        const users = await response.json();
        return users;
    };

    const create_room = async (new_room_name) => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/room', {
            method: 'POST',
            body: JSON.stringify({ room_name: new_room_name }), // string or object
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const myJson = await response.text();
    };

    const invite_room = async (room_id, usernames) => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/room/' + room_id + '/users', {
            method: 'POST',
            body: JSON.stringify({ users: usernames }), // string or object
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const myJson = await response.text();
    };

    const delete_room = async (room_id) => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/room/' + room_id, {
            method: 'DELETE'
        });
        const myJson = await response.text();
    };

    // function render_messages() {
    //     get_room(current_room_id).then(room => {
    //         jQuery.each(room.messages, function () {
    //             if (this.user_id == current_user_id)
    //                 append_receiver_chat_box(this.message, this.datetime);
    //             else
    //                 append_sender_chat_box(this.message, this.datetime, this.username);
    //         });
    //     });
    // }

    function render_messages(messages) {
        jQuery.each(messages, function () {
            if (this.user_id == current_user_id)
                append_receiver_chat_box(this.message, this.datetime);
            else
                append_sender_chat_box(this.message, this.datetime, this.username);
        });
    }

    function load_room_list(activate_room_id) {
        get_room_list().then(rooms => {
            jQuery.each(rooms, function () {
                append_room_list(this.id, this.name, this.owner_id, activate_room_id == this.id);
            });
        });
    }

    function append_sender_chat_box(message, datetime, username) {
        $('div.chat-box').append(
            `
            <div class="media w-50 mb-3"><img
                    src="https://res.cloudinary.com/mhmd/image/upload/v1564960395/avatar_usae7z.svg" alt="user"
                    width="50" class="rounded-circle">
                <div class="media-body ml-3">
                    <div class="bg-light rounded py-2 px-3 mb-2">
                        <p class="text-small font-weight-bold">` + username + `</p>
                        <p class="text-small mb-0 text-muted">` + message + `</p>
                    </div>
                    <p class="small text-muted font-weight-light">` + datetime + `</p>
                </div>
            </div>
            `
        );
    }

    function append_receiver_chat_box(message, datetime) {
        $('div.chat-box').append(
            `
            <div class="media w-50 ml-auto mb-3">
                <div class="media-body">
                    <div class="bg-primary rounded py-2 px-3 mb-2">
                        <p class="text-small mb-0 text-white">` + message + `</p>
                    </div>
                    <p class="small text-muted">` + datetime + `</p>
                </div>
            </div>
            `
        );
    }

    function append_room_list(id, name, owner_id, activate) {
        if (activate) {
            $('div#room-list').append(
                `
                <a href="` + id + `" class="room active list-group-item list-group-item-action rounded-0" data-room-id="`
                + id + `" data-room-name="` + name + `" data-room-owner-id="` + owner_id + `">
                    <div class="media">
                        <div class="media-body ml-2">
                            <div class="d-flex align-items-center justify-content-between mb-1">
                                <h6 class="mb-0">` + name + `</h6>
                                <i class="fa fa-circle text-primary d-none" style="font-size:10px;"></i>
                            </div>
                        </div>
                    </div>
                </a>
                `
            );
        }
        else {
            $('div#room-list').append(
                `
                <a href="` + id + `" class="room list-group-item list-group-item-action list-group-item-light rounded-0" data-room-id="`
                + id + `" data-room-name="` + name + `" data-room-owner-id="` + owner_id + `">
                    <div class="media">
                        <div class="media-body ml-2">
                            <div class="d-flex align-items-center justify-content-between mb-1">
                                <h6 class="mb-0">` + name + `</h6>
                                <i class="fa fa-circle text-primary d-none" style="font-size:10px;"></i>
                            </div>
                        </div>
                    </div>
                </a>
                `
            );
        }
    }

    function scroll_bottom(id) {
        var chat_box = document.getElementById(id);
        chat_box.scrollTop = chat_box.scrollHeight;
    }

    init();
});