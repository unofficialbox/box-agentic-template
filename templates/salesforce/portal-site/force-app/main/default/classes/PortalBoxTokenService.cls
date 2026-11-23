/**
 * GET /services/apexrest/portal/box-token?recordId=<id>[&fileId=<id>]
 *
 * Without fileId: the customer-visible file list plus a token that can only upload into
 * the record's upload folder (scope base_upload). With fileId: a preview-only token for
 * that one file (scope base_preview), after checking the file is in the visible list.
 * The parent token and the Box client secret never leave the server.
 */
@RestResource(urlMapping='/portal/box-token/*')
global with sharing class PortalBoxTokenService {
    private static final String TOKEN_EXCHANGE_GRANT = 'urn:ietf:params:oauth:grant-type:token-exchange';
    private static final String ACCESS_TOKEN_TYPE = 'urn:ietf:params:oauth:token-type:access_token';

    @HttpGet
    global static void token() {
        RestResponse response = RestContext.response;
        response.addHeader('Content-Type', 'application/json');
        response.addHeader('Cache-Control', 'no-store');
        if (PortalBoxAccess.isGuest()) {
            fail(401, 'not_authenticated', 'Sign in to see your documents.');
            return;
        }
        Id recordId;
        try {
            recordId = Id.valueOf(RestContext.request.params.get('recordId'));
        } catch (Exception e) {
            fail(400, 'invalid_record_id', 'recordId is required.');
            return;
        }
        if (PortalBoxAccess.record(recordId) == null) {
            fail(404, 'record_not_found', 'No accessible record matches that ID.');
            return;
        }
        String folderId = PortalBoxDocuments.folderFor(recordId);
        if (String.isBlank(folderId)) {
            fail(404, 'no_box_folder_mapping', 'No Box folder is linked to this record yet.');
            return;
        }
        String fileId = RestContext.request.params.get('fileId');
        try {
            String parent = PortalBoxAuth.parentToken();
            if (String.isBlank(parent)) {
                fail(500, 'box_not_configured', 'Set Portal Box Config and the Portal_Box external credential.');
                return;
            }
            PortalBoxDocuments.Workspace ws = PortalBoxDocuments.workspace(folderId, parent);
            Map<String, Object> payload = new Map<String, Object>{ 'folderId' => folderId };
            if (String.isNotBlank(fileId)) {
                if (!fileId.isNumeric() || !PortalBoxDocuments.containsFile(ws, fileId)) {
                    fail(403, 'file_not_allowed', 'That document is not available here.');
                    return;
                }
                payload.putAll(downscope(parent, 'files/' + fileId, 'base_preview'));
            } else {
                payload.putAll(downscope(parent, 'folders/' + ws.uploadFolderId, 'base_upload'));
                payload.put('uploadFolderId', ws.uploadFolderId);
                payload.put('files', ws.files);
            }
            if (payload.get('accessToken') == null) {
                fail(500, 'box_downscope_failed', 'Box did not return a limited token.');
                return;
            }
            response.statusCode = 200;
            response.responseBody = Blob.valueOf(JSON.serialize(payload));
        } catch (Exception e) {
            // Never echo Box bodies or tokens.
            fail(500, 'box_request_failed', e.getTypeName());
        }
    }

    @TestVisible
    private static Map<String, Object> downscope(String parentToken, String resource, String scopes) {
        HttpResponse res = PortalBoxAuth.post(
            'grant_type=' + EncodingUtil.urlEncode(TOKEN_EXCHANGE_GRANT, 'UTF-8')
            + '&subject_token=' + EncodingUtil.urlEncode(parentToken, 'UTF-8')
            + '&subject_token_type=' + EncodingUtil.urlEncode(ACCESS_TOKEN_TYPE, 'UTF-8')
            + '&scope=' + EncodingUtil.urlEncode(scopes, 'UTF-8')
            + '&resource=' + EncodingUtil.urlEncode('https://api.box.com/2.0/' + resource, 'UTF-8'));
        if (res.getStatusCode() != 200) return new Map<String, Object>();
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        return new Map<String, Object>{
            'accessToken' => body.get('access_token'), 'expiresIn' => body.get('expires_in'), 'scope' => scopes
        };
    }

    private static void fail(Integer status, String error, String detail) {
        RestContext.response.statusCode = status;
        RestContext.response.responseBody = Blob.valueOf(JSON.serialize(new Map<String, String>{ 'error' => error, 'detail' => detail }));
    }
}
