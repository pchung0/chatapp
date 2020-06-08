$(document).ready(function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var current_room_id;
    var current_room_name;
    var current_user_id = $('#username').attr('data-user-id');

    function init() {
        render_room_list();
        if (window.location.pathname.match(/^\/room\/[0-9]+$/g)) {
            current_room_id = window.location.pathname.split("/").slice(-1)[0];
            $('.invite-modal').removeClass('d-none');
            render_messages();
        }
    }

    $("#invite-input").on("keyup", function () {
        var value = $(this).val().toLowerCase();
        $(".dropdown-menu a").filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $('.dropdown-menu').find('a').click(function (e) {
        e.preventDefault();
        var param = $(this).html();
        $('#invite-input').before('<span class="badge badge-secondary align-self-center mr-1">' + param + '</span>');
        $('input').val('');
        $('#invite-input').load("#invite-input");
    });

    $("#invite-input").keydown(function (e) {
        if (e.which == 8 && $(this).val() == '')
            $(this).prev().remove();
    });

    $('.modal').on('shown.bs.modal', function () {
        $(this).find('input').focus();

        if ($(this).attr('id') == 'invite-modal') {
            $('#username-drop-down').empty();
            get_not_in_room_users(current_room_id).then(users => {
                console.log(users);
                jQuery.each(users, function () {
                    $('#username-drop-down').append('<a class="dropdown-item" href="#">' + this.username + '</a>')
                });
            });
        }
    })

    $('div#room-list').on('click', 'a.room', function (e) {
        e.preventDefault();
        current_room_id = parseInt($(this).attr('href'));
        current_room_name = $(this).attr('data-room-name');

        $('#room-list a.active').addClass('list-group-item-light').removeClass('active');
        $(this).addClass('active').removeClass('list-group-item-light');
        $('div.chat-box').empty();

        $('.current-room').text(current_room_name);
        $('.invite-modal').removeClass('d-none');

        render_messages();
        history.pushState('data to be passed', '', '/room/' + current_room_id);
    });

    socket.on('connect', function () {
        console.log('connected:')
        socket.emit('my event', {
            data: 'User Connected'
        })
    })

    var form = $('#message-form').on('submit', function (e) {
        e.preventDefault()
        if (current_room_id) {
            let user_input = $('#message-input-box').val()
            if (user_input) {
                socket.emit('send', {
                    user_name: '{{ current_user.username }}',
                    user_id: current_user_id,
                    room_id: current_room_id,
                    message: user_input
                })
            }
        }
        $('#message-input-box').val('').focus()
    })

    $("#invite").click(function () {
        var users = [];
        $(".input-holder span").each(function () { users.push($(this).text()) });
        socket.emit('invite', {
            room_id: current_room_id,
            users: users
        })
        $('#invite-modal').modal('hide');
    })

    $('#create').click(function () {
        let room_name = $('#create-room-input').val();
        socket.emit('create', room_name);
        $('#create-modal').modal('hide');
        socket.on('redirect room', function (room_id) {
            // $('div.message_holder').append('<div><b style="color: #000">' + msg + '</b></div>')
            window.location.replace('http://' + document.domain + ':' + location.port + '/room/' + room_id);
        })
    })

    $('#confirm-delete').on('show.bs.modal', function (e) {
        $(this).find('.btn-ok').click(function () {
            console.log(current_room_id);
            socket.emit('delete', {
                room_id: current_room_id,
            })
            $('#confirm-delete').modal('hide');
            $('#room-list a.active').remove()
        });

    });

    $('#join').click(function () {
        let room = $('#room').val()
        socket.emit('join', room)
        $('h2#roomname').text(room)
        $('#room').val('')
    })

    $("#leave").click(function () {
        socket.emit('leave')
        // $('h2#roomname').text('')
    })

    socket.on('room info', function (rooms) {
        // $('div.message_holder').append('<div><b style="color: #000">' + msg + '</b></div>')
        console.log(rooms)
    })

    socket.on('message', function (msg) {
        console.log("{{ url_for('home') }}" + '/room')
        console.log(current_room_id, msg.room_id)
        if (current_room_id == msg.room_id) {
            if (current_user_id == msg.user_id)
                append_receiver_chat_box(msg.message, msg.datetime);
            else
                append_sender_chat_box(msg.message, msg.datetime);
            scroll_bottom('chat-box');
        }
    })

    const get_room_list = async () => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/room_list');
        const room_list = await response.json();
        return room_list;
    }

    const get_messages = async (room_id) => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/room/' + room_id + '/messages');
        const messages = await response.json();
        return messages;
    }

    const get_users = async () => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/users');
        const users = await response.json();
        return users;
    }

    const get_not_in_room_users = async (room_id) => {
        const response = await fetch('http://' + document.domain + ':' + location.port + '/room/' + room_id + '/' + 'not_members');
        const users = await response.json();
        return users;
    }

    function render_messages() {
        get_messages(current_room_id).then(messages => {
            jQuery.each(messages, function () {
                if (this.user_id == current_user_id)
                    append_receiver_chat_box(this.message, this.datetime);
                else
                    append_sender_chat_box(this.message, this.datetime);
            });
        });
    }

    function render_room_list() {
        get_room_list().then(rooms => {
            jQuery.each(rooms, function () {
                append_room_list(this.id, this.name, current_room_id == this.id);
            });
        });
    }

    function append_sender_chat_box(message, datetime) {
        $('div.chat-box').append(
            `
            <div class="media w-50 mb-3"><img
                    src="https://res.cloudinary.com/mhmd/image/upload/v1564960395/avatar_usae7z.svg" alt="user"
                    width="50" class="rounded-circle">
                <div class="media-body ml-3">
                    <div class="bg-light rounded py-2 px-3 mb-2">
                        <p class="text-small mb-0 text-muted">` + message + `</p>
                    </div>
                    <p class="small text-muted">` + datetime + `</p>
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

    function append_room_list(id, name, activate) {
        if (activate) {
            $('div#room-list').append(
                `
                <a href="` + id + `" class="room active list-group-item list-group-item-action rounded-0">
                    <div class="media">
                        <div class="media-body ml-2">
                            <div class="d-flex align-items-center justify-content-between mb-1">
                                <h6 class="mb-0">` + name + `</h6>
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
                <a href="` + id + `" class="room list-group-item list-group-item-action list-group-item-light rounded-0" data-room-id="` + id + `" data-room-name="` + name + `">
                    <div class="media">
                        <div class="media-body ml-2">
                            <div class="d-flex align-items-center justify-content-between mb-1">
                                <h6 class="mb-0">` + name + `</h6>
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
})