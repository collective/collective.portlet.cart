// Dependencies: $, cookie_functions.js

(function($) {

    $(document).ready(function() {
        if ($('.disable_max_article_count').length) {
            CART_MAX_ARTICLE_COUNT = 100000;
        }
        cart.init();
        cart.query();
    });
    
    var CART_HIDE_CONTAINER_IF_EMPTY = false;
    var CART_CONTAINER_IDENTIFYER = '#portlet-cart';
    var CART_MAX_ARTICLE_COUNT = 5;
    
    function Cart() {}
    
    Cart.prototype.messages = {
        article_limit_reached: "Die gewünschte Bestellmenge übersteigt die " +
              "maximale Bestellmenge für diesen Artikel.",
        total_limit_reached: "Die gewünschte Bestellmenge übersteigt die " +
              "maximale Gesamtbestellmenge.",
        not_a_number: "Die Eingabe muss eine Ganzzahl sein"
    }
    
    Cart.prototype.init = function() {
        this.cart_node = $('#cart').get(0);
        if (!this.cart_node) {
            return;
        }
        var item_template = $('#card_item_template .cart_item',
                              this.cart_node).get(0);
        this.item_template = $(item_template).clone();
        $('#card_item_template').remove();
    }
    
    Cart.prototype.add = function(uid, count) {
        if (!this.validateOverallCountAdd(count)) {
            return;
        }
        this.writecookie(uid, count, true);
        this.query();
    }
    
    Cart.prototype.set = function(uid, count) {
        if (!this.validateOverallCountSet(uid, count)) {
            return;
        }
        this.writecookie(uid, count, false);
        this.query();
    }
    
    Cart.prototype.writecookie = function(uid, count, inc) {
        count = new Number(count);
        var items = this.items();
        var existent = false;
        for (var item in items) {
            if (!item) {
                continue;
            }
            if (uid == item) {
                if (inc) {
                    items[item] += count;
                } else {
                    items[item] = count;
                }
                existent = true;
                break;
            }
        }
        if (!existent) {
            items[uid] = new Number(count);
        }
        var cookie = '';
        for (var item in items) {
            if (!item || items[item] == 0) {
                continue;
            }
            cookie = cookie + item + ':' + new String(items[item]) + ',';
        }
        if (cookie) {
            cookie = cookie.substring(0, cookie.length - 1);
        }
        createCookie('cart', cookie);
    }
    
    Cart.prototype.render = function(data) {
        if (data['cart_items'].length == 0) {
            if (!CART_HIDE_CONTAINER_IF_EMPTY) {
                $(CART_CONTAINER_IDENTIFYER).css('display', 'block');
            }
            $('#cart_items', this.cart_node).css('display', 'none');
            $('#cart_no_items', this.cart_node).css('display', 'block');
            $('#cart_summary', this.cart_node).css('display', 'none');
        } else {
            $(CART_CONTAINER_IDENTIFYER).css('display', 'block');
            $('#cart_no_items', this.cart_node).css('display', 'none');
            $('#cart_items', this.cart_node).empty();
            $('#cart_items', this.cart_node).css('display', 'block');
            for (var i = 0; i < data['cart_items'].length; i++) {
                var cart_item = $(this.item_template).clone();
                for (var item in data['cart_items'][i]) {
                    var css = '.' + item;
                    var attribute = '';
                    if (item.indexOf(':') != -1) {
                        attribute = item.substring(item.indexOf(':') + 1,
                                                   item.length);
                        css = css.substring(0, item.indexOf(':') + 1);
                    }
                    var value = data['cart_items'][i][item];
                    var placeholder = $(css, cart_item);
                    $(placeholder).each(function(e) {
                        if (attribute != '') {
                            $(this).attr(attribute, value);
                        } else if (this.tagName.toUpperCase() == 'INPUT') {
                            $(this).attr('value', value);
                            $(this).val(value);
                        } else {
                            var idx = $(this).attr(
                                          'class').indexOf('cart_item_count');
                            if (idx == -1) {
                                // no count placeholder
                                $(this).html(value);
                            } else {
                                // if count placeholder in template has 'style'
                                // attribute 'display' set to 'none', do not
                                // change the value. This is necessary items
                                // removal from cart.
                                var mode = $(this).css('display');
                                if (mode == 'inline') {
                                    $(this).html(value);
                                }
                            }
                        }
                    });
                }
                $('#cart_items', this.cart_node).append(cart_item);
            }
            var cart_summary = $('#cart_summary', this.cart_node).get(0);
            for (var item in data['cart_summary']) {
                var css = '.' + item;
                var value = data['cart_summary'][item];
                $(css, cart_summary).html(value);
            }
            $('#cart_summary', this.cart_node).css('display', 'block');
        }
    }
    
    Cart.prototype.bind = function() {
        $('.add_cart_item').each(function() {
            $(this).unbind('click');
            $(this).bind('click', function(e) {
                var defs = cart.extract(this);
                if (cart.validateInt(defs[1])) {
                    var uid = defs[0];
                    var count = defs[1];
                    var items = cart.items();
                    for (var item in items) {
                        if (uid == item) {
                            count = parseInt(count) + parseInt(items[item]);
                            break;
                        }
                    }
                    var url = 'validateItemCount?uid=' + defs[0];
                    url = url + '&count=' + count;
                    bdajax.request({
                        url: url,
                        type: 'json',
                        success: function(data) {
                            if (data == false) {
                                var msg;
                                msg = cart.messages['article_limit_reached'];
                                bdajax.info(unescape(msg));
                            } else {
                                cart.add(defs[0], defs[1]);
                            }
                        }
                    });
                }
                return false;
            });
        });
        $('.update_cart_item').each(function() {
            $(this).unbind('click');
            $(this).bind('click', function(e) {
                var defs = cart.extract(this);
                if (cart.validateInt(defs[1])) {
                    var url = 'validateItemCount?uid=' + defs[0];
                    url = url + '&count=' + defs[1];
                    bdajax.request({
                        url: url,
                        type: 'json',
                        success: function(data) {
                            if (data == false) {
                                var msg;
                                msg = cart.messages['article_limit_reached'];
                                bdajax.info(unescape(msg));
                            } else {
                                cart.set(defs[0], defs[1]);
                            }
                        }
                    });
                }
                return false;
            });
        });
    }
    
    Cart.prototype.extract = function(node) {
        var parent_node = $(node).parent();
        var uid = $('.cart_item_uid', parent_node).text();
        var count_node = $('.cart_item_count', parent_node).get(0);
        var count;
        if (count_node.tagName.toUpperCase() == 'INPUT') {
            count = $(count_node).val();
        } else {
            count = $(count_node).text();
        }
        return [uid, count];
    }
    
    Cart.prototype.validateInt = function(count) {
        if (isNaN(parseInt(count))) {
            bdajax.info(cart.messages['not_a_number']);
            return false;
        }
        return true;
    }
    
    Cart.prototype.cookie = function() {
        var cookie = readCookie('cart');
        if (cookie == null) {
            cookie = '';
        }
        return cookie;
    }
    
    Cart.prototype.items = function() {
        var cookie = this.cookie();
        var cookieitems = cookie.split(',');
        var items = new Object();
        for (var i = 0; i < cookieitems.length; i++) {
            var item = cookieitems[i].split(':');
            items[item[0]] = new Number(item[1]);
        }
        return items;
    }
    
    Cart.prototype.validateOverallCountAdd = function(addcount) {
        var count = 0;
        var items = this.items();
        for (var item in items) {
            if (!item) {
                continue;
            }
            count += parseInt(items[item]);
        }
        count += parseInt(addcount);
        if (count > CART_MAX_ARTICLE_COUNT) {
            var msg;
            msg = cart.messages['total_limit_reached'];
            bdajax.info(unescape(msg));
            return false;
        }
        return true;
    }
    
    Cart.prototype.validateOverallCountSet = function(uid, setcount) {
        var count = 0;
        var items = this.items();
        for (var item in items) {
            if (!item || uid == item) {
                continue;
            }
            count += parseInt(items[item]);
        }
        count += parseInt(setcount);
        if (count > CART_MAX_ARTICLE_COUNT) {
            var msg;
            msg = cart.messages['total_limit_reached']
            bdajax.info(unescape(msg));
            return false;
        }
        return true;
    }
    
    Cart.prototype.query = function() {
        if (!this.cart_node) {
            return;
        }
        if (document.location.href.indexOf('/portal_factory/') != -1) {
            return;
        }
        var url = 'cartData?items=' + this.cookie();
        bdajax.request({
            url: url,
            type: 'json',
            success: function(data) {
                 cart.render(data);
                 cart.bind();
            }
        });
    }
    var cart = new Cart();

})(jQuery);