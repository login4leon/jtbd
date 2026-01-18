
// 使用jQuery重写所有交互功能
$(document).ready(function() {
    let activeMenu = null;
    let isUserMenuOpen = false;

    // 创建菜单HTML模板
    function createActionMenu() {
        return `
            <div class="action-menu">
                <div class="action-menu-item rename-btn">
                    <i class="fas fa-edit"></i>
                    <span>重命名</span>
                </div>
                <div class="action-menu-item duplicate-btn">
                    <i class="fas fa-copy"></i>
                    <span>复制对话</span>
                </div>
                <div class="action-menu-item delete-btn delete">
                    <i class="fas fa-trash"></i>
                    <span>删除</span>
                </div>
            </div>
        `;
    }

    // 关闭操作菜单函数
    function closeActionMenu() {
        if (activeMenu) {
            activeMenu.removeClass('show');
            setTimeout(() => {
                activeMenu.remove();
                activeMenu = null;
            }, 200);
        }
    }

    // 切换用户菜单函数
    function toggleUserMenu() {
        const $settingsMenu = $('#settings-menu');
        const $userInfo = $('#user-toggle');

        isUserMenuOpen = !isUserMenuOpen;

        if (isUserMenuOpen) {
            $settingsMenu.addClass('show');
            $userInfo.addClass('active');
        } else {
            $settingsMenu.removeClass('show');
            $userInfo.removeClass('active');
        }
    }

    // 关闭用户菜单函数
    function closeUserMenu() {
        if (isUserMenuOpen) {
            $('#settings-menu').removeClass('show');
            $('#user-toggle').removeClass('active');
            isUserMenuOpen = false;
        }
    }

    // 历史记录点击效果
    $('.history-item').on('click', function(e) {
        // 如果点击的是操作按钮区域，不执行切换操作
        if ($(e.target).closest('.history-actions').length) {
            return;
        }

        // 移除所有active类
        $('.history-item').removeClass('active');
        // 给当前项添加active类
        $(this).addClass('active');

        // 更新主内容区域显示当前选择的聊天
        const title = $(this).find('.history-title').text();
        const id = $(this).data('id');
        $('.main-content h1').text(title);
        $('.main-content p').html(
            `正在显示聊天记录 #${id}: <strong>${title}</strong><br><br>这是模拟的聊天内容区域，实际应用中这里会显示完整的对话记录。`
        );
    });

    // 新建聊天按钮功能
    $('.new-chat-btn').on('click', function() {
        // 重置所有历史记录的active状态
        $('.history-item').removeClass('active');

        // 更新主内容区域
        $('.main-content h1').text('新对话');
        $('.main-content p').html(
            '开始一个新的对话<br><br>在这里输入您的问题，DeepSeek AI助手将为您提供专业的回答。'
        );

        // 显示提示信息
        alert('已创建新对话，开始与DeepSeek AI聊天吧！');
    });

    // 清除历史记录功能
    $('.clear-history').on('click', function() {
        if (confirm('确定要清除所有聊天历史记录吗？此操作不可撤销。')) {
            const $todayList = $('.history-list').first();
            const $yesterdayHeader = $('.history-header:nth-of-type(2)');
            const $earlierHeader = $('.history-header:nth-of-type(3)');

            // 清除所有历史记录
            $todayList.empty();
            $yesterdayHeader.hide();
            $earlierHeader.hide();

            alert('聊天历史记录已清除！');
        }
    });

    // 用户菜单切换
    $('#user-toggle').on('click', function(e) {
        e.stopPropagation();
        toggleUserMenu();
    });

    // 设置菜单项点击效果
    $('.settings-item').on('click', function(e) {
        e.stopPropagation();
        const action = $(this).data('action');

        // 根据不同设置项执行不同操作
        if (action === 'theme') {
            // 切换深色/浅色模式
            $('body').toggleClass('dark-mode');
            const isDark = $('body').hasClass('dark-mode');

            // 更新按钮文本
            const $button = $(this).find('span');
            $button.text(isDark ? '浅色模式' : '深色模式');

            // 更新图标
            const $icon = $(this).find('i');
            $icon.toggleClass('fa-moon fa-sun');

            if (isDark) {
                $('body').css({
                    backgroundColor: '#1a1a1a',
                    color: '#f0f0f0'
                });

                $('.main-content h1').css('color', '#f0f0f0');
                $('.main-content p').css('color', '#ccc');
                $('.left-navbar').css({
                    backgroundColor: '#2d2d2d',
                    borderRightColor: '#444'
                });
                $('.logo-container').css('borderBottomColor', '#444');
                $('.user-section').css({
                    backgroundColor: '#333',
                    borderTopColor: '#444'
                });
                $('.new-chat-btn').css('boxShadow', '0 4px 12px rgba(0, 0, 0, 0.3)');

                // 更新历史记录项背景
                $('.history-item').each(function() {
                    if ($(this).hasClass('active')) {
                        $(this).css('backgroundColor', '#3a3a3a');
                    } else if ($(this).is(':hover')) {
                        $(this).css('backgroundColor', '#3a3a3a');
                    }
                });
            } else {
                $('body').css({
                    backgroundColor: '#f5f5f5',
                    color: '#333'
                });

                $('.main-content h1').css('color', '#333');
                $('.main-content p').css('color', '#666');
                $('.left-navbar').css({
                    backgroundColor: '#fff',
                    borderRightColor: '#e0e0e0'
                });
                $('.logo-container').css('borderBottomColor', '#f0f0f0');
                $('.user-section').css({
                    backgroundColor: '#fafafa',
                    borderTopColor: '#f0f0f0'
                });
                $('.new-chat-btn').css('boxShadow', '0 4px 12px rgba(107, 115, 255, 0.2)');

                // 更新历史记录项背景
                $('.history-item').each(function() {
                    if ($(this).hasClass('active')) {
                        $(this).css('backgroundColor', '#f0f2ff');
                    } else if ($(this).is(':hover')) {
                        $(this).css('backgroundColor', '#f7f7ff');
                    }
                });
            }
        } else if (action === 'logout') {
            if (confirm('确定要退出登录吗？')) {
                alert('已退出登录，正在跳转到登录页面...');
                // 这里可以添加跳转逻辑
            }
        } else {
            alert(`已选择: ${$(this).find('span').text()}`);
        }

        // 点击后关闭用户菜单
        closeUserMenu();
    });

    // 操作菜单功能
    $('.more-btn').on('click', function(e) {
        e.stopPropagation();

        // 关闭用户菜单（如果打开）
        closeUserMenu();

        // 如果已有操作菜单打开，先关闭
        if (activeMenu) {
            closeActionMenu();
        }

        // 创建新菜单
        const $menuContainer = $('#action-menu-container');
        $menuContainer.html(createActionMenu());
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
            const id = $historyItem.data('id');

            // 为菜单项添加点击事件
            $menu.find('.rename-btn').on('click', function(e) {
                e.stopPropagation();

                const newTitle = prompt('请输入新的对话标题:', title);
                if (newTitle && newTitle.trim() !== '') {
                    $historyItem.find('.history-title').text(newTitle.trim());
                    alert(`对话 #${id} 已重命名为: ${newTitle.trim()}`);
                }

                closeActionMenu();
            });

            $menu.find('.duplicate-btn').on('click', function(e) {
                e.stopPropagation();

                // 在实际应用中，这里会复制对话内容
                alert(`对话 #${id} 已复制，可以在新标签中打开`);
                closeActionMenu();
            });

            $menu.find('.delete-btn').on('click', function(e) {
                e.stopPropagation();

                if (confirm(`确定要删除对话 "${title}" 吗？`)) {
                    $historyItem.css({
                        opacity: '0.5',
                        transform: 'translateX(-20px)'
                    });

                    setTimeout(() => {
                        $historyItem.remove();
                        alert(`对话 #${id} 已删除`);

                        // 如果没有更多历史记录，更新显示
                        if ($('.history-item').length === 0) {
                            $('.main-content h1').text('无聊天记录');
                            $('.main-content p').html(
                                '暂无聊天历史记录，点击"新对话"按钮开始聊天。'
                            );
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

    // 点击页面其他位置关闭用户菜单
    $(document).on('click', function(e) {
        // 如果点击的不是用户区域或设置菜单
        if (!$(e.target).closest('.user-section').length && !$(e.target).closest('.settings-item').length) {
            closeUserMenu();
        }
    });

    // 悬停时自动显示...按钮
    $('.history-item').on('mouseenter', function() {
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
    });

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

    // 窗口大小变化时关闭所有菜单
    $(window).on('resize', function() {
        closeActionMenu();
        closeUserMenu();
    });
});