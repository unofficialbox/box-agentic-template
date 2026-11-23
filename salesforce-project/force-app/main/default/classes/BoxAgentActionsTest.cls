/**
 * Coverage for the seeded Agentforce action stubs. Seeded once by scripts/build_agent.py;
 * extend it as you implement each action.
 */
@IsTest
private class BoxAgentActionsTest {
    @IsTest
    static void get_recordReportsMissingAdapter() {
        List<BoxAgentGetRecord.Response> responses = BoxAgentGetRecord.run(new List<BoxAgentGetRecord.Request>{ new BoxAgentGetRecord.Request() });
        System.assert(responses[0].result.contains('live_adapter_not_implemented'));
    }

    @IsTest
    static void search_documentsReportsMissingAdapter() {
        List<BoxAgentSearchDocuments.Response> responses = BoxAgentSearchDocuments.run(new List<BoxAgentSearchDocuments.Request>{ new BoxAgentSearchDocuments.Request() });
        System.assert(responses[0].result.contains('live_adapter_not_implemented'));
    }

    @IsTest
    static void analyze_documentReportsMissingAdapter() {
        List<BoxAgentAnalyzeDocument.Response> responses = BoxAgentAnalyzeDocument.run(new List<BoxAgentAnalyzeDocument.Request>{ new BoxAgentAnalyzeDocument.Request() });
        System.assert(responses[0].result.contains('live_adapter_not_implemented'));
    }

    @IsTest
    static void propose_updateReportsMissingAdapter() {
        List<BoxAgentProposeUpdate.Response> responses = BoxAgentProposeUpdate.run(new List<BoxAgentProposeUpdate.Request>{ new BoxAgentProposeUpdate.Request() });
        System.assert(responses[0].result.contains('live_adapter_not_implemented'));
    }

    @IsTest
    static void verify_generated_documentReportsMissingAdapter() {
        List<BoxAgentVerifyGeneratedDocument.Response> responses = BoxAgentVerifyGeneratedDocument.run(new List<BoxAgentVerifyGeneratedDocument.Request>{ new BoxAgentVerifyGeneratedDocument.Request() });
        System.assert(responses[0].result.contains('live_adapter_not_implemented'));
    }
}
