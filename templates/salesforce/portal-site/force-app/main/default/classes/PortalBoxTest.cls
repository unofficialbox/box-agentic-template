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

    @IsTest
    static void signRequestNeedsInputs() {
        PortalBoxSendForSignature.Request req = new PortalBoxSendForSignature.Request();
        List<PortalBoxSendForSignature.Result> results = PortalBoxSendForSignature.prepare(new List<PortalBoxSendForSignature.Request>{ req });
        System.assertEquals(false, results[0].prepared);
    }
}
