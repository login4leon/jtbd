// State management
let cases = [];
let messages = [];
let ideas = [];
let isProcessing = false;
let activeMenu = null;
let CASE_ID;
let PRODUCT;
let INFO;
let USER_ID;

// DOM elements (jQuery objects)
let $titleSection;
let $productInput;
let $infoInput;
let $sendButton;
let $messagesContainer;
let $ideasContainer;
let $caseList;
let $messageTitle;
let $ideaTitle;
let $productHeader;
let $infoHeader;
let $userButton;
let $userDropdown;
let $newButton;

// Initialize when DOM is ready
$(document).ready(function () {
    // Get DOM elements using jQuery
    $titleSection = $('#titleSection');
    $productInput = $('#productInput');
    $infoInput = $('#infoInput');
    $sendButton = $('#sendButton');
    $messagesContainer = $('#messagesContainer');
    $ideasContainer = $('#ideasContainer');
    $caseList = $('#caseList');
    $messageTitle = $('#messageTitle');
    $ideaTitle = $('#ideaTitle');
    $productHeader = $('#productHeader');
    $infoHeader = $('#infoHeader');
    $userButton = $('#userButton');
    $userDropdown = $('#userDropdown');
    $newButton = $('#newButton');

    // 获取user_id
    USER_ID = $userButton.attr('uid');

    // 隐藏过程和结果的Title
    $messageTitle.hide();
    $ideaTitle.hide();

    // Event listeners using jQuery
    $sendButton.on('click', handleSubmit);
    $productInput.on('input', updateSendButton);
    $infoInput.on('input', updateSendButton);

    // Enter key support
    $infoInput.on('keydown', function (e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleSubmit();
        }
    });

    // 点击用户出现菜单，点击空白收起菜单
    $userButton.on('click', function (e) {
        e.stopPropagation();

        const rect = $userButton[0].getBoundingClientRect();
        $userDropdown.removeClass('hide').addClass('show');
        const mh = $userDropdown.outerHeight();

        $userDropdown.css({
            left: rect.right,
            top: rect.top - mh
        });
    });

    $(document).on('click', function () {
        $userDropdown.removeClass('show').addClass('hide');
    });

    // 开启新发现
    $newButton.on('click', function () {
        location.reload();
    })

    // 获取用户历史记录
    listCase();


    // Initialize
    updateSendButton();
});

function updateSendButton() {
    const hasProduct = $productInput.val().trim() !== '';
    const hasInfo = $infoInput.val().trim() !== '';
    $sendButton.prop('disabled', !hasProduct || !hasInfo || isProcessing);
    $newButton.prop('disabled', isProcessing);
    $userButton.prop('disabled', isProcessing)
    $caseList.find('.conversation-item').prop('disabled', isProcessing);
}

function listCase() {
    $.ajax({
        url: '/jtbd/listcase/',
        type: 'GET',
        data: {
            user_id: USER_ID
        },
        dataType: 'JSON',
        success: function (res) {
            if (res.status) {
                cases = res.cases;
                renderCases();
            }
        }
    });
}

function addCase() {
    const c = {
        id: CASE_ID,
        product: PRODUCT,
        info: INFO,
        start_time: new Date(),
        closed: false
    };
    cases.unshift(c);
    renderCases();
    updateSendButton();
}

function pinSvg() {
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512">
                <path d="M32 32C32 14.3 46.3 0 64 0L320 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-29.5 0 11.4 148.2c36.7 19.9 65.7 53.2 79.5 94.7l1 3c3.3 9.8 1.6 20.5-4.4 28.8s-15.7 13.3-26 13.3L32 352c-10.3 0-19.9-4.9-26-13.3s-7.7-19.1-4.4-28.8l1-3c13.8-41.5 42.8-74.8 79.5-94.7L93.5 64 64 64C46.3 64 32 49.7 32 32zM160 384l64 0 0 96c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-96z"/>
            </svg>`;
}

function unpinSvg() {
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512">
                <path d="M38.8 5.1C28.4-3.1 13.3-1.2 5.1 9.2S-1.2 34.7 9.2 42.9l592 464c10.4 8.2 25.5 6.3 33.7-4.1s6.3-25.5-4.1-33.7L481.4 352c9.8-.4 18.9-5.3 24.6-13.3c6-8.3 7.7-19.1 4.4-28.8l-1-3c-13.8-41.5-42.8-74.8-79.5-94.7L418.5 64 448 64c17.7 0 32-14.3 32-32s-14.3-32-32-32L192 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l29.5 0-6.1 79.5L38.8 5.1zM324.9 352L177.1 235.6c-20.9 18.9-37.2 43.3-46.5 71.3l-1 3c-3.3 9.8-1.6 20.5 4.4 28.8s15.7 13.3 26 13.3l164.9 0zM288 384l0 96c0 17.7 14.3 32 32 32s32-14.3 32-32l0-96-64 0z"/>
            </svg>`;
}

function closeSvg() {
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                <path d="M438.6 105.4c12.5 12.5 12.5 32.8 0 45.3l-256 256c-12.5 12.5-32.8 12.5-45.3 0l-128-128c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0L160 338.7 393.4 105.4c12.5-12.5 32.8-12.5 45.3 0z"/>
            </svg>`;
}

function runSvg() {
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                <path d="M304 48a48 48 0 1 0 -96 0 48 48 0 1 0 96 0zm0 416a48 48 0 1 0 -96 0 48 48 0 1 0 96 0zM48 304a48 48 0 1 0 0-96 48 48 0 1 0 0 96zm464-48a48 48 0 1 0 -96 0 48 48 0 1 0 96 0zM142.9 437A48 48 0 1 0 75 369.1 48 48 0 1 0 142.9 437zm0-294.2A48 48 0 1 0 75 75a48 48 0 1 0 67.9 67.9zM369.1 437A48 48 0 1 0 437 369.1 48 48 0 1 0 369.1 437z"/>
            </svg>`;
}

function itemHtml(c) {
    return `<li class="history-item" data-case-id="${c.id}" data-case-product="${c.product}" data-case-info="${c.info}" data-case-closed="${c.closed}" data-case-pinned="${c.pinned}">
            <div class="case-row">
                <div class="case-item">
                    <span class="status-icon">
                        ${c.pinned ? pinSvg() : c.closed ? closeSvg() : runSvg()}
                    </span>
                    <span class="history-title">${c.product}</span>
                    <span class="time-stamp">${c.info}</span>
                </div>
                
            </div>
            <div class="history-actions">
                <button class="more-btn" title="更多操作">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                        <path d="M8 256a56 56 0 1 1 112 0A56 56 0 1 1 8 256zm160 0a56 56 0 1 1 112 0 56 56 0 1 1 -112 0zm216-56a56 56 0 1 1 0 112 56 56 0 1 1 0-112z"/></svg>
                </button>
            </div>
        </li>`;
}

function renderCases() {
    let caseHtml = '';
    cases.forEach(block => {
        caseHtml += `
            <div class="history-block" data-key="${block.key}">
                <div class="history-header">${block.title}</div>
                <ul class="case-list">
                    ${block.list.map(c => itemHtml(c)).join('')}
                </ul>
            </div>`;
    });

    $caseList.html(caseHtml);
    if (CASE_ID) {
        const $btn = $('li.history-item[data-case-id="${CASE_ID}"]');
        $btn.addClass('active');
    }

    // Attach click handlers using jQuery event delegation
    $caseList.find('.history-item').on('click', function () {
        const $btn = $(this);
        const id = $btn.data('case-id');
        const product = $btn.data('case-product')
        const info = $btn.data('case-info');
        const closed = $btn.data('case-closed');
        // 移除所有active类
        $('.history-item').removeClass('active');
        // 给当前项添加active类
        $(this).addClass('active');
        selectCase(id, product, info, closed);
    });
    // 悬停时自动显示...按钮
    $caseList.find('.history-item').on('mouseenter', function() {
        if ($(this).data('case-closed')) {
            const $actions = $(this).find('.history-actions');
            if ($actions.length) {
                // 确保鼠标进入时按钮可见
                setTimeout(() => {
                    $actions.css({
                        opacity: '1',
                        visibility: 'visible'
                    });
                }, 50);
            }
        }
    });
    // 鼠标离开时，...按钮消失
    $('.history-item').on('mouseleave', function(e) {
        // 如果鼠标移动到操作按钮或菜单上，不要隐藏
        const relatedTarget = e.relatedTarget;
        const $actions = $(this).find('.history-actions');

        if ($actions.length && !$actions.is(relatedTarget) && $actions.has(relatedTarget).length === 0
            && (!activeMenu || !activeMenu.is(relatedTarget) && activeMenu.has(relatedTarget).length === 0)) {
            $actions.css({
                opacity: '0',
                visibility: 'hidden'
            });
        }
    });
    // 设置点击...按钮
    $('.more-btn').on('click', function(e) {
        e.stopPropagation();

        // 如果已有操作菜单打开，先关闭
        if (activeMenu) {
            closeActionMenu();
        }

        // 创建新菜单
        const $menuContainer = $('#action-menu-container');
        const isPinned = $(this).closest('.history-item').data('case-pinned');
        $menuContainer.html(createActionMenu(isPinned));
        const $menu = $menuContainer.find('.action-menu');


        // 获取按钮位置
        const buttonRect = $(this)[0].getBoundingClientRect();

        // 设置菜单位置：在按钮右侧，与按钮顶部对齐
        $menu.css({
            left: `${buttonRect.right + 5}px`,
            top: `${buttonRect.top}px`
        });

        // 显示菜单
        setTimeout(() => {
            $menu.addClass('show');
            activeMenu = $menu;

            // 获取相关数据
            const $historyItem = $(this).closest('.history-item');
            const title = $historyItem.find('.history-title').text();
            const id = $historyItem.data('case-id');

            // 为菜单项添加点击事件
            $menu.find('.pin-btn').on('click', function(e) {
                e.stopPropagation();

                $.ajax({
                    url: '/jtbd/pincase/',
                    type: 'GET',
                    data: {
                        case_id: id
                    },
                    dataType: 'JSON',
                    success: function (res) {
                        if (res.status) {
                            listCase();
                        }
                    }
                });

                closeActionMenu();
            });

            $menu.find('.delete-btn').on('click', function(e) {
                e.stopPropagation();

                if (confirm(`确定要删除本记录 "${title}" 吗？`)) {
                    $historyItem.css({
                        opacity: '0.5',
                        transform: 'translateX(-20px)'
                    });

                    setTimeout(() => {
                        $.ajax({
                            url: '/jtbd/delcase/',
                            type: 'GET',
                            data: {
                                case_id: id
                            },
                            dataType: 'JSON',
                            success: function (res) {
                                if (res.status) {
                                    alert(`${title} 已删除`);
                                    listCase();
                                }
                            }
                        });


                        // 如果没有更多历史记录，更新显示
                        if ($('.history-item').length === 0) {
                            location.reload();
                        }
                    }, 300);
                }

                closeActionMenu();
            });

            // 点击菜单外部关闭菜单
            $(document).on('click.closeActionMenu', function(e) {
                if ($menu.length && !$menu.is(e.target) && $menu.has(e.target).length === 0
                    && !$(e.target).closest('.more-btn').length) {
                    closeActionMenu();
                    $(document).off('click.closeActionMenu');
                }
            });

            // 菜单内部点击不关闭菜单
            $menu.on('click', function(e) {
                e.stopPropagation();
            });
        }, 10);
    });
}

function selectCase(id, product, info, closed) {
    $titleSection.hide();
    // 根据case是否closed，分别执行
    if (closed === true) {
        showCase(id);
    } else {
        closeCase(id, product, info);
    }
}

function showCase(id) {
    // 联系后端，获取对应（case_id）结果
    $.ajax({
            url: '/jtbd/output/',
            type: 'GET',
            data: {
                case_id: id
            },
            dataType: 'JSON',
            success: function (out) {
                if (out.status) {
                    // 展示标题
                    const opening1 = '产品：' + out.case.product;
                    const opening2 = '产品描述：' + out.case.info;
                    $productHeader.text(opening1);
                    $infoHeader.text(opening2);
                    //展示结果
                    renderIdeas(out.ideas);
                }
            }
    });
}

async function closeCase(id, product, info) {
    // 清空并隐藏操作过程展示和结果展示的区域，以便后面依次展示
    messages = [];
    $ideasContainer.empty();
    $messagesContainer.empty();
    $productHeader.empty();
    $infoHeader.empty();
    $ideaTitle.hide();
    $messageTitle.hide();

    CASE_ID = id;
    PRODUCT = product;
    INFO = info;

    if (!PRODUCT || !INFO || isProcessing) return;

    isProcessing = true;
    $productInput.prop('disabled', true);
    $infoInput.prop('disabled', true);
    updateSendButton();

    // 开始展示操作过程
    $messageTitle.show();
    const opening1 = '产品：' + PRODUCT;
    const opening2 = '产品描述：' + INFO;
    $productHeader.text(opening1);
    $infoHeader.text(opening2);
    addMessage('继续分析您的产品...', isProcessing);
    // 展示过程信息
    flowProcessing();

    // 向后台发起操作流程
    await $.ajax({
        url: '/jtbd/work/',
        type: 'GET',
        data: {
            case_id: CASE_ID
        },
        dataType: 'JSON',
        success: function (out) {
            if (out.status) {
                // 展示结果
                renderIdeas(out.ideas); //展示结果
                listCase(USER_ID);
            }
        }
    });

    // Reset form using jQuery
    isProcessing = false;
    $productInput.val('');
    $infoInput.val('');
    $productInput.prop('disabled', false);
    $infoInput.prop('disabled', false);
    updateSendButton();
}

function createActionMenu(isPinned) {
    const pinText = isPinned ? '取消置顶' : '置顶';
    const pinIcon = isPinned ? unpinSvg() : pinSvg();
    const pinClass = isPinned ? 'pin-btn' : 'pin-btn';

    return `
        <div class="action-menu">
            <div class="action-menu-item ${pinClass} pin-action-btn">
                <span class="status-icon">
                    ${pinIcon}
                </span>
                <span>${pinText}</span>
            </div>
            <div class="action-menu-item delete-btn delete">
                <span class="status-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                        <path d="M135.2 17.7C140.6 6.8 151.7 0 163.8 0L284.2 0c12.1 0 23.2 6.8 28.6 17.7L320 32l96 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 96C14.3 96 0 81.7 0 64S14.3 32 32 32l96 0 7.2-14.3zM32 128l384 0 0 320c0 35.3-28.7 64-64 64L96 512c-35.3 0-64-28.7-64-64l0-320zm96 64c-8.8 0-16 7.2-16 16l0 224c0 8.8 7.2 16 16 16s16-7.2 16-16l0-224c0-8.8-7.2-16-16-16zm96 0c-8.8 0-16 7.2-16 16l0 224c0 8.8 7.2 16 16 16s16-7.2 16-16l0-224c0-8.8-7.2-16-16-16zm96 0c-8.8 0-16 7.2-16 16l0 224c0 8.8 7.2 16 16 16s16-7.2 16-16l0-224c0-8.8-7.2-16-16-16z"/>
                    </svg>
                </span>
                <span>删除</span>
            </div>
        </div>
    `;
}

function closeActionMenu() {
    if (activeMenu) {
        activeMenu.removeClass('show');
        setTimeout(() => {
            activeMenu.remove();
            activeMenu = null;
        }, 200);
    }
}

function addMessage(content, isProcessingMsg = false) {
    const message = {
        id: Date.now().toString(),
        content: content,
        isProcessing: isProcessingMsg,
    };
    messages.push(message);
    renderMessages();
    return message;
}

function renderMessages() {

    const messagesHtml = messages.map(message => {

            if (message.isProcessing !== undefined) {
                return `
                    <div class="message">
                        <div class="message-content">
                            <div class="processing-message">
                                <p style="margin: 0;">${escapeHtml(message.content)}</p>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                return `
                    <div class="message">
                        <div class="message-content">${formatMessageContent(message.content)}</div>
                    </div>
                `;
            }
        }
    ).join('');

    $messagesContainer.html(messagesHtml);

    // Scroll to bottom using jQuery
    $messagesContainer.scrollTop($messagesContainer[0].scrollHeight);
}

function renderIdeas(ideass) {
    let ideasHtml = `
                            <table class="table table-bordered">
                                <thead>
                                <tr>
                                    <th>机会点</th>
                                    <th>目标人群</th>
                                    <th>产品设计</th>
                                    <th>营销口号</th>
                                </tr>
                                </thead>
                                <tbody>
                        `;


    ideasHtml += ideass.map(idea => {
            return `
                    <tr>
                        <td style="font-size: 12px;">${idea.opportunity}</td>
                        <td style="font-size: 12px;">${idea.customer}</td>
                        <td style="font-size: 12px;">${idea.design}</td>
                        <td style="font-size: 12px;">${idea.slogan}</td>
                    </tr>
                `;
        }
    ).join('');

    ideasHtml += `
                    </tbody>
                    </table>
                `;
    $ideaTitle.show();
    $ideasContainer.html(ideasHtml);

// Scroll to bottom using jQuery
    $ideasContainer.scrollTop($ideasContainer[0].scrollHeight);
}

function escapeHtml(text) {
    return $('<div>').text(text).html();
}

function formatMessageContent(content) {
    // Simple markdown-like formatting for **bold**
    let formatted = escapeHtml(content);
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
}

function flowProcessing() {

    const source = new EventSource(`/sse/stream/?case_id=` + CASE_ID);
    source.onmessage = function (e) {
        if (e.data === '[DONE]') {
            source.close();
            return;
        }
        const chunk = JSON.parse(e.data);
        addMessage(chunk.text, isProcessing);
    }
}

async function handleSubmit() {

    // 清空并隐藏操作过程展示和结果展示的区域，以便后面依次展示
    messages = [];
    $titleSection.hide();
    $ideasContainer.empty();
    $messagesContainer.empty();
    $productHeader.empty();
    $infoHeader.empty();
    $ideaTitle.hide();
    $messageTitle.hide();

    PRODUCT = $productInput.val().trim();
    INFO = $infoInput.val().trim();

    if (!PRODUCT || !INFO || isProcessing) return;

    isProcessing = true;
    $productInput.prop('disabled', true);
    $infoInput.prop('disabled', true);
    updateSendButton();

    // 向后台发送数据，新建case，返回case_id
    await $.ajax({
        url: '/jtbd/opencase/',
        type: 'GET',
        data: {
            product: PRODUCT,
            info: INFO,
            user_id: USER_ID
        },
        dataType: 'JSON',
        success: function (res) {
            if (res.status) {
                CASE_ID = res.case;
            }
        }
    });
    // 更新历史记录
    listCase();
    // 开始展示操作过程
    $messageTitle.show();
    const opening1 = '产品：' + PRODUCT;
    const opening2 = '产品描述：' + INFO;
    $productHeader.text(opening1);
    $infoHeader.text(opening2);
    addMessage('开始分析您的产品...', isProcessing);
    // 展示过程信息
    flowProcessing();

    // 向后台发起操作流程
    await $.ajax({
        url: '/jtbd/work/',
        type: 'GET',
        data: {
            case_id: CASE_ID
        },
        dataType: 'JSON',
        success: function (out) {
            if (out.status) {
                // 展示结果
                renderIdeas(out.ideas); //展示结果
            }
        }
    });

    // Reset form using jQuery
    isProcessing = false;
    $productInput.val('');
    $infoInput.val('');
    $productInput.prop('disabled', false);
    $infoInput.prop('disabled', false);
    updateSendButton();
    renderCases();
}