
let CONTACTS = [];
let GROUPS = [];
let ACTIVE_CONV = null;

$(document).ready(function () {
    init();

    setInterval(refreshMessages, 3000);

    $('#send-btn').click(sendMessage);
    $('#message-input').keypress(function (e) {
        if (e.which == 13 && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    $('#search-input').on('input', function () {
        renderSidebar($(this).val());
    });
});

function init() {
    $.get('/api/init_data', function (data) {
        CONTACTS = data.contacts;
        GROUPS = data.groups;
        renderSidebar();
    });
}

function renderSidebar(filter = '') {
    const list = $('#contact-list');
    list.empty();
    filter = filter.toLowerCase();

    // Render Groups
    if (GROUPS.length > 0) {
        list.append(`<div class="sidebar-section-title">Groups</div>`);
        GROUPS.forEach(group => {
            if (group.toLowerCase().includes(filter)) {
                const isActive = (ACTIVE_CONV && ACTIVE_CONV.type === 'group' && ACTIVE_CONV.target === group) ? 'active' : '';
                const html = `
                    <div class="contact-item ${isActive}" onclick="selectConversation('${group}', 'group', '${group}')">
                        <div class="avatar group-avatar">📢</div>
                        <div class="contact-info">
                            <div class="contact-name">${group}</div>
                            <div class="contact-preview">Department Broadcast</div>
                        </div>
                    </div>
                `;
                list.append(html);
            }
        });
    }

    // Render Individuals
    if (CONTACTS.length > 0) {
        list.append(`<div class="sidebar-section-title">Contacts</div>`);
        CONTACTS.forEach(contact => {
            if (contact.name.toLowerCase().includes(filter) || contact.phone.includes(filter)) {
                const isActive = (ACTIVE_CONV && ACTIVE_CONV.type === 'individual' && ACTIVE_CONV.target === contact.phone) ? 'active' : '';
                const initial = contact.name.charAt(0).toUpperCase();
                const html = `
                    <div class="contact-item ${isActive}" onclick="selectConversation('${contact.phone}', 'individual', '${contact.name}')">
                        <div class="avatar">${initial}</div>
                        <div class="contact-info">
                            <div class="contact-name">${contact.name}</div>
                            <div class="contact-preview">${contact.phone}</div>
                        </div>
                    </div>
                `;
                list.append(html);
            }
        });
    }
}

function selectConversation(target, type, name) {
    ACTIVE_CONV = { target, type, name };
    $('#chat-placeholder').hide();
    $('#chat-interface').css('display', 'flex');
    $('#chat-name').text(name);
    $('#chat-details').text(type === 'group' ? 'Broadcast Group' : target);
    renderSidebar($('#search-input').val());
    fetchMessages();

    // Auto focus on input
    $('#message-input').focus();
}

function fetchMessages() {
    if (!ACTIVE_CONV) return;
    $.get(`/api/messages?target=${encodeURIComponent(ACTIVE_CONV.target)}&type=${ACTIVE_CONV.type}`, function (messages) {
        renderMessages(messages);
    });
}

function refreshMessages() {
    if (ACTIVE_CONV) fetchMessages();
}

function renderMessages(messages) {
    const container = $('#messages-container');
    container.empty();

    if (messages.length === 0) {
        container.append('<div class="no-messages">No messages yet.</div>');
        return;
    }

    messages.forEach(msg => {
        const msgClass = 'sent';
        let subInfo = `${msg.time} • ${msg.status}`;
        if (ACTIVE_CONV.type === 'group') subInfo += ` → ${msg.recipient}`;

        const html = `
            <div class="message-bubble ${msgClass}">
                ${msg.text}
                <div class="message-info">${subInfo}</div>
            </div>
        `;
        container.append(html);
    });
}

function sendMessage() {
    if (!ACTIVE_CONV) return;
    const text = $('#message-input').val().trim();
    if (!text) return;
    $('#message-input').val('');

    $.ajax({
        url: "/api/send",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ target: ACTIVE_CONV.target, message: text, type: ACTIVE_CONV.type }),
        success: function () { fetchMessages(); },
        error: function () { alert("Error sending message"); }
    });
}

// Quick Send Function
function sendDirectMessage() {
    const phone = $('#quick-phone').val().trim();
    const msg = $('#quick-message').val().trim();

    if (!phone || !msg) {
        alert("Please enter both phone number and message.");
        return;
    }

    // Send it
    $.ajax({
        url: "/api/send",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ target: phone, message: msg, type: 'individual' }),
        success: function () {
            // After sending, open the chat for this number
            // Check if contact exists to get name, otherwise use phone as name
            const existing = CONTACTS.find(c => c.phone === phone);
            const name = existing ? existing.name : phone;

            // If contact doesn't exist, maybe we should prompt to save? Or just show as unsaved.
            // For now, switch to chat interface
            selectConversation(phone, 'individual', name);

            // Clear inputs
            $('#quick-phone').val('');
            $('#quick-message').val('');
        },
        error: function () { alert("Error sending message"); }
    });

}

// Modal Logic
function openAddContact() { $('#contact-modal').addClass('active'); }
function closeAddContact() { $('#contact-modal').removeClass('active'); }
function openGroupModal() { $('#group-modal').addClass('active'); }
function closeGroupModal() { $('#group-modal').removeClass('active'); }

function saveContact() {
    const name = $('#new-name').val();
    const phone = $('#new-phone').val();
    const dept = $('#new-dept').val();

    if (!name || !phone) return alert("Name/Phone required");
    $.ajax({
        url: "/api/contacts",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ name, phone_number: phone, department: dept }),
        success: function () {
            closeAddContact();
            init();
            $('#new-name').val('');
            $('#new-phone').val('');
        }
    });
}

function sendGroup() {
    const dept = $('#group-dept').val();
    const msg = $('#group-msg').val();
    if (!msg) return;
    $.ajax({
        url: "/api/send",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ target: dept, message: msg, type: 'group' }),
        success: function () {
            alert("Group command sent!");
            closeGroupModal();
            $('#group-msg').val('');
        }
    });
}
