(function($) {
    "use strict";

    function html_unescape(value){
        return String(value)
            .replace(/&quot;/g, '"')
            .replace(/&#39;/g, "'")
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&amp;/g, '&');
    }

    function add_remove() {
        var classes = this.classList;
        classes.contains('member')
            ? (classes.contains('remove')
                ? $(this).removeClass('remove')
                : $(this).addClass('remove'))
            : (classes.contains('add')
                ? $(this).removeClass('add')
                : $(this).addClass('add'));
    }

    function submit_post() {
        var add = $('.add');
        var adds = [];
        add.map(function(idx, el) {
            adds.push(el.id);
        });

        var remove = $('.remove');
        var removes = [];
        remove.map(function(idx, el) {
            removes.push(el.id);
        });

        var csrftoken = $.cookie('csrftoken');

        var data = {}
        data['adds'] = adds;
        data['removes'] = removes;
        data['csrfmiddlewaretoken'] = csrftoken;

        console.log(data);

        $.post(URL, data).done(function(response) {
            var len = window.location.href.length - "edit/".length
            window.location.href = window.location.href.substring(0,len)
        });
    }

    function cancel() {
        window.location.href = window.location.origin + window.location.pathname.substring(0,10)
    }

    $(function() {
        var members = JSON.parse(html_unescape(members_str));
        var others = JSON.parse(html_unescape(others_str));

        var list = $('div.member-list');

        members.map(function(person) {
            var tile = $('<div>', { id: person.pk, class: 'tile member' });

            var pic = $('<div>', { class: 'table-edit-pic' });
            var img = $('<img>', { class: 'profile-pic' }).attr('src', person.fields.profile_picture_url);
            pic.append(img);

            var stats = $('<div>', { class: 'table-edit-stats' });
            var ul = $('<ul>', { class: 'table-edit-stats' });
            ul.append($('<li>', { text: person.fields.full_name }));
            ul.append($('<li>', { text: person.fields.username }));
            stats.append(ul);

            tile.append(pic);
            tile.append(stats);

            list.append(tile);
        });

        list = $('div.other-list');

        others.map(function(person) {
            var tile = $('<div>', { id: person.pk, class: 'tile other' });

            var pic = $('<div>', { class: 'table-edit-pic' });
            var img = $('<img>', { class: 'profile-pic' }).attr('src', person.fields.profile_picture_url);
            pic.append(img);

            var stats = $('<div>', { class: 'table-edit-stats' });
            var ul = $('<ul>', { class: 'table-edit-stats' });
            ul.append($('<li>', { text: person.fields.full_name }));
            ul.append($('<li>', { text: person.fields.username }));
            stats.append(ul);

            tile.append(pic);
            tile.append(stats);

            list.append(tile);
        });

        $('div.tile').on('click', add_remove);

        $('.save').on('click', submit_post);

        $('.cancel').on('click', cancel);

    });

})(jQuery);


    // <div class="tile member">
    //     <div class="table-edit-pic">
    //         <img src="{{ member.picture_profile_url }}" />
    //     </div>
    //     <div>
    //         <ul class="table-edit-stats">
    //             <li>{{ member.full_name }}</li>
    //             <li>{{ member.username }}</li>
    //         </ul>
    //     </div>
    // </div>
