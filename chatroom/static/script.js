$(document).ready(function () {
    console.log('{{ room_id }}')
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var current_room_id = -1;

    socket.on('connect', function () {
        console.log('connected:')
        socket.emit('my event', {
            data: 'User Connected'
        })
    })

    var form = $('#message-form').on('submit', function (e) {
        e.preventDefault()
        let user_input = $('#message-input-box').val()
        socket.emit('send', {
            user_name: '{{ current_user.username }}',
            user_id: '{{ current_user.id }}',
            room_id: '{{ room_id }}',
            message: user_input
        })
        $('#message-input-box').val('').focus()
        $('div.chat-box').append(
            `
            <div class="media w-50 ml-auto mb-3">
                <div class="media-body">
                    <div class="bg-primary rounded py-2 px-3 mb-2">
                        <p class="text-small mb-0 text-white">`+user_input+`</p>
                    </div>
                    <p class="small text-muted">12:00 PM | Aug 13</p>
                </div>
            </div>
            `)
    })

    $('#join').click(function () {
        let room = $('#room').val()
        socket.emit('join', room)
        $('h2#roomname').text(room)
        $('#room').val('')
    })

    $('#create').click(function () {
        let room = $('#room').val()
        socket.emit('create', room)
        // $('h2#roomname').text(room)
        $('#room').val('')
    })

    $("#leave").click(function () {
        socket.emit('leave')
        // $('h2#roomname').text('')
    })

    $(".room").click(function () {
        current_room_id = $(this).text()
        $('h2#roomname').text(current_room_id)
    })

    socket.on('room info', function (rooms) {
        // $('div.message_holder').append('<div><b style="color: #000">' + msg + '</b></div>')
        console.log(rooms)
    })

    socket.on('message', function (data) {
        console.log("{{ url_for('home') }}" + '/room')
        console.log('{{ room_id }}', data.room_id)
        if ('{{ room_id }}' == data.room_id && '{{ current_user.id }}' != data.user_id) {
            $('div.chat-box').append(
            `
            <div class="media w-50 mb-3"><img
                    src="https://res.cloudinary.com/mhmd/image/upload/v1564960395/avatar_usae7z.svg" alt="user"
                    width="50" class="rounded-circle">
                <div class="media-body ml-3">
                    <div class="bg-light rounded py-2 px-3 mb-2">
                        <p class="text-small mb-0 text-muted">`+data.message+`</p>
                    </div>
                    <p class="small text-muted">12:00 PM | Aug 13</p>
                </div>
            </div>
            `)
        }
    })

    socket.on('my response', function (msg) {
        if (typeof msg.user_name !== 'undefined') {
            $('div.message_holder').append(
            `
            <div class="media w-50 mb-3"><img
                    src="https://res.cloudinary.com/mhmd/image/upload/v1564960395/avatar_usae7z.svg" alt="user"
                    width="50" class="rounded-circle">
                <div class="media-body ml-3">
                    <div class="bg-light rounded py-2 px-3 mb-2">
                        <p class="text-small mb-0 text-muted">test</p>
                    </div>
                    <p class="small text-muted">12:00 PM | Aug 13</p>
                </div>
            </div>
            `)
        }
    })
})