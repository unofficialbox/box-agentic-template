/**
 * Creates a Box Sign request with embedded signing for a document in the record's Box
 * folder, and stores the signer's iframe URL and the request ID on the record so the
 * customer can sign inside the portal. For employees, Flows, and agents; never exposed to
 * customers. Signature fields come from Box Sign tags in the document.
 */
public with sharing class PortalBoxSendForSignature {
    private static final String SIGN_ENDPOINT = 'callout:Portal_Box/2.0/sign_requests';

    public class Request {
        @InvocableVariable(label='Record ID' required=true)
        public String recordId;
        @InvocableVariable(label='Box file ID' description='A file in the record\'s Box folder' required=true)
        public String fileId;
        @InvocableVariable(label='Signer email' required=true)
        public String signerEmail;
        @InvocableVariable(label='Signer name')
        public String signerName;
        @InvocableVariable(label='Email subject')
        public String subject;
    }

    public class Result {
        @InvocableVariable(label='Outcome')
        public String summary;
        @InvocableVariable(label='Prepared')
        public Boolean prepared;
        @InvocableVariable(label='Box Sign request ID')
        public String requestId;
    }

    @InvocableMethod(label='Create Box Sign request for portal signing'
        description='Creates a Box Sign request with embedded signing for a file in the record folder and stores the signing URL on the record for the portal.')
    public static List<Result> prepare(List<Request> requests) {
        List<Result> results = new List<Result>();
        for (Request req : requests) {
            results.add(prepareOne(req));
        }
        return results;
    }

    private static Result prepareOne(Request req) {
        Result result = new Result();
        result.prepared = false;
        if (!PortalBoxSettings.signEnabled()) {
            result.summary = 'Box Sign is not configured for the portal. Nothing was sent.';
            return result;
        }
        if (req == null || String.isBlank(req.recordId) || String.isBlank(req.fileId) || String.isBlank(req.signerEmail)) {
            result.summary = 'A record, a Box file, and a signer email are required. Nothing was sent.';
            return result;
        }
        Id recordId;
        try { recordId = Id.valueOf(req.recordId); }
        catch (Exception e) { result.summary = 'That is not a Salesforce record ID.'; return result; }
        SObject record = PortalBoxAccess.record(recordId);
        String folderId = record == null ? null : PortalBoxDocuments.folderFor(recordId);
        if (String.isBlank(folderId)) {
            result.summary = 'The record is not accessible or has no Box folder. Nothing was sent.';
            return result;
        }
        try {
            String token = PortalBoxAuth.parentToken();
            if (!inFolder(req.fileId.trim(), folderId, token)) {
                result.summary = 'That file is not in this record\'s Box folder, so it was not sent.';
                return result;
            }
            HttpRequest httpReq = new HttpRequest();
            httpReq.setEndpoint(SIGN_ENDPOINT);
            httpReq.setMethod('POST');
            httpReq.setHeader('Content-Type', 'application/json');
            httpReq.setHeader('Authorization', 'Bearer ' + token);
            httpReq.setTimeout(60000);
            Map<String, Object> signer = new Map<String, Object>{
                'email' => req.signerEmail.trim(), 'role' => 'signer', 'embed_url_external_user_id' => req.signerEmail.trim() };
            if (String.isNotBlank(req.signerName)) signer.put('name', req.signerName.trim());
            httpReq.setBody(JSON.serialize(new Map<String, Object>{
                'source_files' => new List<Object>{ new Map<String, Object>{ 'id' => req.fileId.trim(), 'type' => 'file' } },
                'parent_folder' => new Map<String, Object>{ 'id' => folderId, 'type' => 'folder' },
                'signers' => new List<Object>{ signer },
                'is_document_preparation_needed' => false,
                'subject' => String.isBlank(req.subject) ? 'Please sign your document' : req.subject.trim() }));
            HttpResponse res = new Http().send(httpReq);
            if (res.getStatusCode() != 200 && res.getStatusCode() != 201) {
                result.summary = 'Box Sign refused the request (' + res.getStatusCode() + '). Nothing was sent.';
                return result;
            }
            Map<String, Object> parsed = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
            result.requestId = String.valueOf(parsed.get('id'));
            String embedUrl;
            for (Object entry : (List<Object>) parsed.get('signers')) {
                Map<String, Object> s = (Map<String, Object>) entry;
                if (req.signerEmail.trim().equalsIgnoreCase((String) s.get('email')) && s.get('role') == 'signer') {
                    embedUrl = (String) s.get('iframeable_embed_url');
                }
            }
            if (String.isBlank(embedUrl)) {
                result.summary = 'Box Sign created request ' + result.requestId + ' without a signing URL. Do not create a duplicate.';
                return result;
            }
            record.put(PortalBoxSettings.SIGN_EMBED_URL_FIELD, embedUrl);
            record.put(PortalBoxSettings.SIGN_REQUEST_ID_FIELD, result.requestId);
            update record;
            result.prepared = true;
            result.summary = 'Box Sign request ' + result.requestId + ' is ready for ' + req.signerEmail.trim() + ' to sign in the portal.';
        } catch (Exception e) {
            result.summary = 'The signature request could not be prepared. Nothing was sent.';
        }
        return result;
    }

    private static Boolean inFolder(String fileId, String folderId, String token) {
        if (!fileId.isNumeric()) return false;
        HttpResponse res = PortalBoxAuth.get('files/' + fileId + '?fields=parent', token);
        if (res.getStatusCode() != 200) return false;
        Map<String, Object> parent = (Map<String, Object>) ((Map<String, Object>) JSON.deserializeUntyped(res.getBody())).get('parent');
        return parent != null && PortalBoxDocuments.folderTree(folderId, token).contains((String) parent.get('id'));
    }
}
