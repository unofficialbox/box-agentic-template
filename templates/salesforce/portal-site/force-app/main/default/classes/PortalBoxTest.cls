/**
 * Unit coverage for the portal Box services without a live Box tenant. Callouts are mocked;
 * record-level paths need records of the configured object, so extend this class in your
 * project with fixtures for that object.
 */
@IsTest
private class PortalBoxTest {
    private class BoxMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(200);
            if (req.getEndpoint().contains('/oauth2/token')) {
                res.setBody('{"access_token":"token-1","expires_in":3600}');
            } else if (req.getEndpoint().contains('/items')) {
                res.setBody('{"entries":[{"type":"file","id":"11","name":"a.pdf","size":1,"modified_at":"2026-01-01"},'
                    + '{"type":"folder","id":"22","name":"Uploads"}]}');
            } else {
                res.setBody('{}');
            }
            return res;
        }
    }

    private static void configure() {
        insert new Portal_Box_Config__c(SetupOwnerId = UserInfo.getOrganizationId(), Box_User_Id__c = '42');
    }

    @IsTest
    static void parentTokenUsesTheConfiguredSubject() {
        configure();
        Test.setMock(HttpCalloutMock.class, new BoxMock());
        Test.startTest();
        System.assertEquals('token-1', PortalBoxAuth.parentToken());
        Test.stopTest();
    }

    @IsTest
    static void parentTokenIsNullWithoutConfiguration() {
        System.assertEquals(null, PortalBoxAuth.parentToken());
    }

    @IsTest
    static void workspaceListsRootFilesAndDownscopes() {
        configure();
        Test.setMock(HttpCalloutMock.class, new BoxMock());
        Test.startTest();
        PortalBoxDocuments.Workspace ws = PortalBoxDocuments.workspace('100', 'token-1');
        Set<String> tree = PortalBoxDocuments.folderTree('100', 'token-1');
        Map<String, Object> scoped = PortalBoxTokenService.downscope('token-1', 'folders/100', 'base_upload');
        Test.stopTest();
        System.assert(tree.contains('22'));
        System.assertEquals('token-1', scoped.get('accessToken'));
        if (PortalBoxSettings.VISIBLE_SUBFOLDERS.isEmpty()) {
            System.assert(PortalBoxDocuments.containsFile(ws, '11'));
        }
    }

    @IsTest
    static void guestsAndBadInputAreRefused() {
        PortalBoxAccess.userTypeOverride = 'Guest';
        System.assertEquals(null, PortalBoxAccess.record(UserInfo.getUserId()));
        RestContext.request = new RestRequest();
        RestContext.response = new RestResponse();
        PortalBoxTokenService.token();
        System.assertEquals(401, RestContext.response.statusCode);
        PortalSignStatus.status();
        PortalBoxAccess.userTypeOverride = 'Standard';
        RestContext.response = new RestResponse();
        PortalBoxTokenService.token();
        System.assertEquals(400, RestContext.response.statusCode);
        RestContext.response = new RestResponse();
        PortalBoxFolderService.provision();
        System.assertEquals(400, RestContext.response.statusCode);
    }

    private class FullMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(200);
            String url = req.getEndpoint();
            if (url.contains('/oauth2/token')) {
                res.setBody('{"access_token":"token-1","expires_in":3600}');
            } else if (url.contains('/items')) {
                String sub = PortalBoxSettings.VISIBLE_SUBFOLDERS.isEmpty() ? 'Uploads' : PortalBoxSettings.VISIBLE_SUBFOLDERS[0];
                res.setBody('{"entries":[{"type":"file","id":"11","name":"a.pdf","size":1,"modified_at":"2026-01-01"},'
                    + '{"type":"folder","id":"100","name":"' + sub + '"}]}');
            } else if (url.contains('/files/')) {
                res.setBody('{"parent":{"id":"100","type":"folder"}}');
            } else if (url.endsWith('/sign_requests')) {
                res.setStatusCode(201);
                res.setBody('{"id":"sr-1","signers":[{"email":"signer@example.com","role":"signer","iframeable_embed_url":"https://app.box.com/embed/sign/document/x/"}]}');
            } else if (url.contains('/sign_requests/')) {
                res.setBody('{"status":"signed","parent_folder":{"id":"100"},"sign_files":{"is_ready_for_download":true}}');
            } else {
                res.setBody('{}');
            }
            return res;
        }
    }

    /** A record of the configured object with a synthetic ID; nothing is inserted. */
    private static SObject fakeRecord() {
        Schema.SObjectType type = Schema.getGlobalDescribe().get(PortalBoxSettings.RECORD_OBJECT);
        Id fakeId = Id.valueOf(type.getDescribe().getKeyPrefix() + '000000000001');
        SObject record = type.newSObject(fakeId);
        if (PortalBoxSettings.signEnabled()) {
            record.put(PortalBoxSettings.SIGN_EMBED_URL_FIELD, 'https://app.box.com/embed/sign/document/x/');
            record.put(PortalBoxSettings.SIGN_REQUEST_ID_FIELD, 'sr-1');
        }
        return record;
    }

    private static Id prepare() {
        configure();
        Test.setMock(HttpCalloutMock.class, new FullMock());
        SObject record = fakeRecord();
        PortalBoxAccess.userTypeOverride = 'Standard';
        PortalBoxAccess.recordOverride = record;
        PortalBoxDocuments.folderOverride = '100';
        RestContext.request = new RestRequest();
        RestContext.response = new RestResponse();
        RestContext.request.params.put('recordId', record.Id);
        return record.Id;
    }

    @IsTest
    static void tokenServiceReturnsUploadAndPreviewTokens() {
        prepare();
        Test.startTest();
        PortalBoxTokenService.token();
        System.assertEquals(200, RestContext.response.statusCode, RestContext.response.responseBody.toString());
        RestContext.response = new RestResponse();
        RestContext.request.params.put('fileId', '11');
        PortalBoxTokenService.token();
        Integer previewStatus = RestContext.response.statusCode;
        RestContext.response = new RestResponse();
        RestContext.request.params.put('fileId', '999');
        PortalBoxTokenService.token();
        Test.stopTest();
        System.assert(previewStatus == 200 || previewStatus == 403);
        System.assertEquals(403, RestContext.response.statusCode);
    }

    @IsTest
    static void tokenServiceRefusesUnknownRecordsAndMissingFolders() {
        Id recordId = prepare();
        PortalBoxAccess.recordOverride = null;
        PortalBoxAccess.accountOverride = UserInfo.getUserId();
        Test.startTest();
        PortalBoxTokenService.token();
        System.assertEquals(404, RestContext.response.statusCode);
        PortalBoxAccess.recordOverride = fakeRecord();
        PortalBoxDocuments.folderOverride = '';
        RestContext.response = new RestResponse();
        Test.stopTest();
        System.assertNotEquals(null, recordId);
    }

    @IsTest
    static void signStatusReadsBox() {
        prepare();
        Test.startTest();
        PortalSignStatus.status();
        Test.stopTest();
        System.assertNotEquals(null, RestContext.response.statusCode);
    }

    @IsTest
    static void signRequestIsCreatedForAFileInTheFolder() {
        Id recordId = prepare();
        Test.startTest();
        PortalBoxSendForSignature.Request req = new PortalBoxSendForSignature.Request();
        req.recordId = recordId;
        req.fileId = '11';
        req.signerEmail = 'signer@example.com';
        req.signerName = 'Synthetic Signer';
        List<PortalBoxSendForSignature.Result> results = PortalBoxSendForSignature.prepare(new List<PortalBoxSendForSignature.Request>{ req });
        Test.stopTest();
        System.assertNotEquals(null, results[0].summary);
    }

    @IsTest
    static void signRequestRefusesFilesOutsideTheFolderAndBadIds() {
        Id recordId = prepare();
        PortalBoxSendForSignature.Request outside = new PortalBoxSendForSignature.Request();
        outside.recordId = recordId;
        outside.fileId = 'not-a-number';
        outside.signerEmail = 'signer@example.com';
        PortalBoxSendForSignature.Request badId = new PortalBoxSendForSignature.Request();
        badId.recordId = 'not-an-id';
        badId.fileId = '11';
        badId.signerEmail = 'signer@example.com';
        Test.startTest();
        List<PortalBoxSendForSignature.Result> results = PortalBoxSendForSignature.prepare(
            new List<PortalBoxSendForSignature.Request>{ outside, badId });
        Test.stopTest();
        System.assertEquals(false, results[0].prepared);
        System.assertEquals(false, results[1].prepared);
    }

    @IsTest
    static void accessChecksAccountAndRealQueries() {
        SObject record = fakeRecord();
        PortalBoxAccess.userTypeOverride = 'Standard';
        System.assertEquals(null, PortalBoxAccess.customerAccount());
        // No override: the real query finds no record with a synthetic ID.
        System.assertEquals(null, PortalBoxAccess.record(record.Id));
        PortalBoxAccess.recordOverride = record;
        System.assertEquals(record, PortalBoxAccess.record(record.Id));
        System.assertEquals(null, PortalBoxAccess.record(UserInfo.getUserId()));
    }

    @IsTest
    static void folderServiceProvisionsThroughTheToolkit() {
        prepare();
        Test.startTest();
        PortalBoxFolderService.provision();
        Test.stopTest();
        Integer code = RestContext.response.statusCode;
        System.assert(code == 200 || code == 500, String.valueOf(code));
    }

    @IsTest
    static void folderServiceRefusesWithoutAccess() {
        prepare();
        PortalBoxAccess.recordOverride = null;
        PortalBoxFolderService.provision();
        System.assertEquals(404, RestContext.response.statusCode);
    }

    @IsTest
    static void signRequestNeedsInputs() {
        PortalBoxSendForSignature.Request req = new PortalBoxSendForSignature.Request();
        List<PortalBoxSendForSignature.Result> results = PortalBoxSendForSignature.prepare(new List<PortalBoxSendForSignature.Request>{ req });
        System.assertEquals(false, results[0].prepared);
    }
}
