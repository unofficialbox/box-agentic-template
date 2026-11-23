/**
 * POST /services/apexrest/portal/box-folder?recordId=<id>
 *
 * Creates the record's Box folder through Box for Salesforce when none exists yet. Separate
 * from the token endpoint because Apex cannot make a callout after DML in one transaction;
 * the portal calls this, then asks for a token again.
 */
@RestResource(urlMapping='/portal/box-folder/*')
global with sharing class PortalBoxFolderService {
    @HttpPost
    global static void provision() {
        RestResponse response = RestContext.response;
        response.addHeader('Content-Type', 'application/json');
        response.addHeader('Cache-Control', 'no-store');
        Id recordId;
        try {
            recordId = Id.valueOf(RestContext.request.params.get('recordId'));
        } catch (Exception e) {
            reply(400, new Map<String, Object>{ 'error' => 'invalid_record_id' });
            return;
        }
        if (PortalBoxAccess.record(recordId) == null) {
            reply(404, new Map<String, Object>{ 'error' => 'record_not_found' });
            return;
        }
        String folderId = new Provisioner().forRecord(recordId);
        if (String.isBlank(folderId)) {
            reply(500, new Map<String, Object>{ 'error' => 'box_folder_not_provisioned' });
            return;
        }
        reply(200, new Map<String, Object>{ 'folderId' => folderId, 'recordId' => recordId });
    }

    private static void reply(Integer status, Map<String, Object> body) {
        RestContext.response.statusCode = status;
        RestContext.response.responseBody = Blob.valueOf(JSON.serialize(body));
    }

    /** Package call after the caller's record access was checked. */
    private without sharing class Provisioner {
        private String forRecord(Id recordId) {
            box.Toolkit toolkit = new box.Toolkit();
            try {
                return toolkit.createFolderForRecordId(recordId, null, true);
            } catch (Exception e) {
                System.debug(LoggingLevel.WARN, 'Portal Box: provisioning failed: ' + e.getMessage());
                return null;
            } finally {
                try {
                    toolkit.commitChanges();
                } catch (Exception commitError) {
                    System.debug(LoggingLevel.WARN, 'Portal Box: commitChanges failed: ' + commitError.getMessage());
                }
            }
        }
    }
}
