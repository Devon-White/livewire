/*
 * call.js
 * Handles SignalWire call widget setup and event handling for the call page (call.html).
 */

async function getWidgetConfig() {
    const resp = await fetch('/api/widget_config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });
    if (!resp.ok) throw new Error('Failed to fetch widget config');
    return await resp.json();
}

function setupCallWidget() {
    const callButton = document.getElementById('callButton');
    if (!callButton) {
        console.error('callButton element not found in the DOM');
        return;
    }

    getWidgetConfig().then(config => {
        // Create the widget element
        const widgetHtml = /*html*/`
            <c2c-widget
                buttonId="${callButton.id}"
                collectUserDetails="false"
                userVariables="{}"
                callDetails='${JSON.stringify({
                    destination: config.destination,
                    supportsVideo: false,
                    supportsAudio: true
                })}'
                token="${config.guest_token}">
            </c2c-widget>
        `;
        
        // Insert the widget HTML after the call button
        callButton.insertAdjacentHTML('afterend', widgetHtml);

        const widget = document.querySelector('c2c-widget');

        // Attach other event listeners as before
        widget.addEventListener("beforecall", () => {
            console.log("beforecall");
            ['ci-SAT', 'pt-SAT', 'as-SAT'].forEach(key => sessionStorage.removeItem(key));
        });
        widget.addEventListener("call.joined", ({ detail }) => {
            detail.client.on("user_event", (params) => {
                if (params.type === "send_user_info") {
                    console.log("send_user_info", params);
                }
            });
            console.log("call.joined", detail);
        });
        widget.addEventListener("call.left", ({ detail }) => console.log("call.left", detail));
    }).catch(err => {
        alert('Failed to get guest token: ' + err.message);
    });
}

document.addEventListener('DOMContentLoaded', setupCallWidget); 