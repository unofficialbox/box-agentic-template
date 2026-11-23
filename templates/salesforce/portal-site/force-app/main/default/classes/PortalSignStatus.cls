/**
 * POST /services/apexrest/portal/sign-status?recordId=<id>
 *
 * Box is the authority on whether a document was signed: the portal polls this endpoint
 * instead of trusting messages from the cross-origin Sign iframe. Returns the Box Sign
 * status (for example sent, viewed, signed, declined, cancelled, expired), "none" when no
 * request is open, or "finalizing" while signed files are still being written. On a final
 * status it clears the stored iframe URL so the portal stops showing the signing frame.
 */
@RestResource(urlMapping='/portal/sign-status/*')
global with sharing class PortalSignStatus {
    private static final Set<String> FINAL_STATUSES = new Set<String>{ 'signed', 'declined', 'cancelled', 'expired' };

    @HttpPost
    global static void status() {
        RestContext.response.addHeader('Content-Type', 'application/json');
        RestContext.response.addHeader('Cache-Control', 'no-store');
        if (!PortalBoxSettings.signEnabled()) { reply(404, 'sign_not_configured'); return; }
        if (PortalBoxAccess.isGuest()) { reply(401, 'unauthorized'); return; }
        Id recordId;
        try { recordId = Id.valueOf(RestContext.request.params.get('recordId')); }
        catch (Exception e) { reply(400, 'invalid_record'); return; }
        SObject record = PortalBoxAccess.record(recordId);
        if (record == null) { reply(404, 'not_found'); return; }
        String embed = (String) record.get(PortalBoxSettings.SIGN_EMBED_URL_FIELD);
        String requestId = (String) record.get(PortalBoxSettings.SIGN_REQUEST_ID_FIELD);
        if (String.isBlank(embed) || String.isBlank(requestId)) { reply(200, 'none'); return; }
        if (!Pattern.matches('[A-Za-z0-9-]+', requestId)) { reply(503, 'invalid_request'); return; }
        try {
            String token = PortalBoxAuth.parentToken();
            HttpResponse res = PortalBoxAuth.get('sign_requests/' + requestId, token);
            if (res.getStatusCode() != 200) { reply(503, 'unavailable'); return; }
            Map<String, Object> payload = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
            String status = (String) payload.get('status');
            if (String.isBlank(status)) { reply(503, 'unavailable'); return; }
            if (status == 'signed') {
                Map<String, Object> parent = (Map<String, Object>) payload.get('parent_folder');
                String folderId = PortalBoxDocuments.folderFor(recordId);
                if (parent == null || String.isBlank(folderId)
                    || !PortalBoxDocuments.folderTree(folderId, token).contains((String) parent.get('id'))) {
                    reply(503, 'folder_mismatch'); return;
                }
                Map<String, Object> signFiles = (Map<String, Object>) payload.get('sign_files');
                if (signFiles == null || signFiles.get('is_ready_for_download') != true) { reply(200, 'finalizing'); return; }
            }
            if (FINAL_STATUSES.contains(status)) {
                SObject current = record.getSObjectType().newSObject(recordId);
                current.put(PortalBoxSettings.SIGN_EMBED_URL_FIELD, null);
                // The caller's access was checked above; customers cannot edit this field themselves.
                Database.update(current, AccessLevel.SYSTEM_MODE);
            }
            reply(200, status);
        } catch (Exception e) {
            reply(503, 'unavailable');
        }
    }

    private static void reply(Integer code, String status) {
        RestContext.response.statusCode = code;
        RestContext.response.responseBody = Blob.valueOf(JSON.serialize(new Map<String, Object>{ 'status' => status }));
    }
}
