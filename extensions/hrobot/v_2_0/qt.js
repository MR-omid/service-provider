Qt = {
    nextIndex: 0,
    nodes: {},

    findXpath: function (xpath) {
        return this.findXpathRelativeTo(document, xpath);
    },

    findXpathRelativeTo: function (reference, xpath) {
        var iterator = document.evaluate(xpath, reference, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);
        var node;
        var results = [];
        while (node = iterator.iterateNext()) {
            results.push(this.registerNode(node));
        }
        return results.join(",");
    },

    findCss: function (selector) {
        return this.findCssRelativeTo(document, selector);
    },

    findCssRelativeTo: function (reference, selector) {
        var elements = reference.querySelectorAll(selector);
        var results = [];
        for (var i = 0; i < elements.length; i++) {
            results.push(this.registerNode(elements[i]));
        }
        return results.join(",");
    },

    registerNode: function (node) {
        this.nextIndex++;
        this.nodes[this.nextIndex] = node;
        return this.nextIndex;
    },

    position: function (index) {
        node = this.getNode(index);
        rect = node.getBoundingClientRect();
        return rect
    },

    centerPosition: function (index) {
        element = this.getNode(index)
        this.reflow(element);
        var rect = element.getBoundingClientRect();
        var position = {
            x: rect.width / 2,
            y: rect.height / 2
        };
        do {
            position.x += element.offsetLeft;
            position.y += element.offsetTop;
        } while ((element = element.offsetParent));
        position.x = Math.floor(position.x);
        position.y = Math.floor(position.y);

        return position;
    },

    reflow: function (element, force) {
        if (force || element.offsetWidth === 0) {
            var prop, oldStyle = {}, newStyle = {position: "absolute", visibility: "hidden", display: "block"};
            for (prop in newStyle) {
                oldStyle[prop] = element.style[prop];
                element.style[prop] = newStyle[prop];
            }
            // force reflow
            element.offsetWidth;
            element.offsetHeight;
            for (prop in oldStyle)
                element.style[prop] = oldStyle[prop];
        }
    },

    isAttached: function (index) {
        return this.nodes[index] &&
            document.evaluate("ancestor-or-self::html", this.nodes[index], null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue != null;
    },

    getNode: function (index) {
        if (this.isAttached(index)) {
            return this.nodes[index];
        } else {
            throw new Qt.NodeNotAttachedError(index);
        }
    },

    text: function (index) {
        var node = this.getNode(index);
        var type = node instanceof HTMLFormElement ? 'form' : (node.type || node.tagName).toLowerCase();

        if (!this.isNodeVisible(node)) {
            return '';
        } else if (type == "textarea") {
            return node.innerHTML;
        } else {
            visible_text = node.innerText;
            return typeof visible_text === "string" ? visible_text : node.textContent;
        }
    },

    visible: function (index) {
        return this.isNodeVisible(this.getNode(index));
    },

    isNodeVisible: function (node) {
        var style = node.ownerDocument.defaultView.getComputedStyle(node, null);
        // Only check computed visibility style on current node since it
        // will inherit from nearest ancestor with a setting and overrides
        // any farther ancestors
        if (style.getPropertyValue('visibility') == 'hidden' || style.getPropertyValue('display') == 'none')
            return false;

        // Must check CSS display setting for all ancestors
        while (node = node.parentElement) {
            style = node.ownerDocument.defaultView.getComputedStyle(node, null);
            if (style.getPropertyValue('display') == 'none')
                return false;
        }
        return true;
    },

    focus: function (index) {
        this.getNode(index).focus();
    },

    path: function (index) {
        return this.pathForNode(this.getNode(index));
    },

    pathForNode: function (node) {
        return "/" + this.getXPathNode(node).join("/");
    },

    getXPathNode: function (node, path) {
        path = path || [];
        if (node.parentNode) {
            path = this.getXPathNode(node.parentNode, path);
        }

        var first = node;
        while (first.previousSibling)
            first = first.previousSibling;

        var count = 0;
        var index = 0;
        var iter = first;
        while (iter) {
            if (iter.nodeType == 1 && iter.nodeName == node.nodeName)
                count++;
            if (iter.isSameNode(node))
                index = count;
            iter = iter.nextSibling;
            continue;
        }

        if (node.nodeType == 1)
            path.push(node.nodeName.toLowerCase() + (node.id ? "[@id='" + node.id + "']" : count > 1 ? "[" + index + "]" : ''));

        return path;
    },

    selectOption: function (index) {
        this._setOption(index, true);
    },

    unselectOption: function (index) {
        this._setOption(index, false);
    },

    _setOption: function (index, state) {
        var optionNode = this.getNode(index);
        var selectNode = optionNode.parentNode;
        if (selectNode.tagName == "OPTGROUP")
            selectNode = selectNode.parentNode;

        if (optionNode.disabled)
            return;

        if ((!selectNode.multiple) && (!state))
            return;

        // click on select list
        this.triggerOnNode(selectNode, 'mousedown');
        selectNode.focus();
        this.triggerOnNode(selectNode, 'input');

        // select/deselect option from list
        if (optionNode.selected != state) {
            optionNode.selected = state;
            this.triggerOnNode(selectNode, 'change');
        }

        this.triggerOnNode(selectNode, 'mouseup');
        this.triggerOnNode(selectNode, 'click');
    },

    trigger: function (index, eventName) {
        this.triggerOnNode(this.getNode(index), eventName);
    },

    triggerOnNode: function (node, eventName) {
        var eventObject = document.createEvent("HTMLEvents");
        eventObject.initEvent(eventName, true, true);
        node.dispatchEvent(eventObject);
    },

    attribute: function (index, name) {
        var node = this.getNode(index);
        if (node.hasAttribute(name)) {
            return node.getAttribute(name);
        }
        return void 0;
    },

    set: function (index, value) {
        var length, maxLength, node, strindex, textTypes, type;
        node = this.getNode(index);
        type = (node.type || node.tagName).toLowerCase();
        textTypes = ["email", "number", "password", "search", "tel", "text", "textarea", "url"];
        if (textTypes.indexOf(type) != -1) {
            maxLength = this.attribute(index, "maxlength");
            if (maxLength && value.length > maxLength) {
                length = maxLength;
            } else {
                length = value.length;
            }
            if (!node.readOnly) {
                this.focus(index);

                node.value = "";
                node.value = value
                // console.error('start typing')
                // for (strindex = 0; strindex < length; strindex++) {
                //     console.error('in typing')
                //     console.error(strindex)
                //     console.error(length)
                    // this.simulateKey(node, value[strindex].charCodeAt(0),'press')
                    // this.simulateKey(node, value[strindex].charCodeAt(0),'down')
                    // this.simulateKey(node, value[strindex].charCodeAt(0),'up')
                    // node.dispatchEvent(new KeyboardEvent('keypress',{'key':value[strindex]}));
                    // var e = document.createEvent('HTMLEvents');
                    //     e.keyCode = value[strindex].charCodeAt(0);
                    //     e.initEvent(type, false, true);
                    //     node.dispatchEvent(e);
                    // console.error(value[strindex])
                // }
            }
        } else if (type === "checkbox" || type === "radio") {
            if (node.checked != (value === "true")) {
                this.click(index);
            }
        } else if (this.isContentEditable(node)) {
            var content = document.createTextNode(value);
            node.innerHTML = '';
            node.appendChild(content);
        } else {
            node.value = value;
        }
        this.trigger(index, "input");
        this.trigger(index, "change");
    },

    enter: function (index) {
        ev = new KeyboardEvent('keydown', {
            altKey: false,
            bubbles: true,
            cancelBubble: false,
            cancelable: true,
            charCode: 0,
            code: "Enter",
            composed: true,
            ctrlKey: false,
            currentTarget: null,
            defaultPrevented: true,
            detail: 0,
            eventPhase: 0,
            isComposing: false,
            isTrusted: true,
            key: "Enter",
            keyCode: 13,
            location: 0,
            metaKey: false,
            repeat: false,
            returnValue: false,
            shiftKey: false,
            type: "keydown",
            which: 13
        });
        node = this.getNode(index)
        node.dispatchEvent(ev)

        // QtInvocation.emit_async_js_finished()
        console.error('after enter')
    },

    click: function (index) {
        node = this.getNode(index)
        node.scrollIntoViewIfNeeded()
        target = node.target
        if(target){
            if(target=='_blank'){
                node.target = '_self'
            }
        }
        node.click()
        QtInvocation.emit_async_js_finished()
        // this.focus(index)
        // this.leftClick(index)
    },

    // leftClick: function (index) {
    //     node = this.getNode(index)
    //     center_position = this.centerPosition(index)
    //     console.error('js start click')
    //     QtInvocation.click(center_position.x, center_position.y)
    //     console.error('js end click')
    //     console.error(this.is_loading)
    //
    // },

    submit: function (index) {
        node = this.getNode(index)
        if (node.tagName.toLowerCase() == 'form')
            node.submit();
    },

    tagName: function (index) {
        return this.getNode(index).tagName.toLowerCase();
    },

    value: function (index) {
        return this.getNode(index).value;
    },

    img2b64: function (index) {
        node = this.getNode(index);
        if (!['image', 'img'].includes(node.tagName.toLowerCase())) {
            console.error('Method:(img2b64) -> this method work for img tag, not (' + node.tagName + ')')
            return
        }

        canvas = document.createElement("canvas");
        canvas.width = node.width;
        canvas.height = node.height;
        ctx = canvas.getContext("2d");
        ctx.drawImage(node, 0, 0);
        return canvas.toDataURL("image/png")
    },

    sleep: async function (ms) {
        return new Promise(resolve => setTimeout(resolve, ms))
    },

    scrollToEnd: async function (lazy_load = true) {
        window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"})
        if (lazy_load) {
            content_size = document.body.scrollHeight
            await this.sleep(3000)
            while (content_size != document.body.scrollHeight) {
                content_size = document.body.scrollHeight
                window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"})
                await this.sleep(3000)
            }
        }
        QtInvocation.emit_async_js_finished()
    },

    getCookies: function() {
        var theCookies = document.cookie.split(';');
        var aString = '';
        for (var i = 1 ; i <= theCookies.length; i++) {
            aString += i + ' ' + theCookies[i-1] + "\n";
        }
        return aString;
    },

    _visitedObjects: [],
    wrapResult: function (arg) {
        if (this._visitedObjects.indexOf(arg) >= 0) {
            return '(cyclic structure)';
        }
        if (arg instanceof NodeList) {
            arg = Array.prototype.slice.call(arg, 0);
        }
        if (Array.isArray(arg)) {
            for (var _j = 0; _j < arg.length; _j++) {
                arg[_j] = this.wrapResult(arg[_j]);
            }
        } else if (arg && arg.nodeType == 1 && arg.tagName) {
            return {'element-581e-422e-8be1-884c4e116226': this.registerNode(arg)};
        } else if (arg === null) {
            return undefined;
        } else if (arg instanceof Date) {
            return arg;
        } else if (typeof arg == 'object') {
            this._visitedObjects.push(arg);
            var result = {};
            for (var _k in arg) {
                result[_k] = this.wrapResult(arg[_k]);
            }
            this._visitedObjects.pop();
            return result;
        }
        return arg;
    }
};

Qt.NodeNotAttachedError = function (index) {
    this.name = 'Qt.NodeNotAttachedError';
    this.message = 'Element at ' + index + ' no longer present in the DOM';
};
Qt.NodeNotAttachedError.prototype = new Error();
Qt.NodeNotAttachedError.prototype.constructor = Qt.NodeNotAttachedError;

// initialize QWebChannel
new QWebChannel(qt.webChannelTransport,
    function (channel) {
        window.QtInvocation = channel.objects.QtInvocation;
        QtInvocation.emit_js_ready()
    });
// window.onbeforeunload = function () {
//     console.error('before unload')
// };
// window.onload = function () {
//     console.error('load')
// };
// window.onunload = function () {
//     console.error('unload')
// };