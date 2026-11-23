/**
 * The record's Box folder and the documents a customer may see in it.
 *
 * The folder comes from the Box for Salesforce association (box.Toolkit), never from the
 * caller. Listing happens on the server with the parent token, so the browser only ever
 * receives the filtered file list and tokens downscoped to one folder or one file.
 */
public with sharing class PortalBoxDocuments {
    public class Workspace {
        public String folderId;
        public String uploadFolderId;
        public List<Map<String, Object>> files = new List<Map<String, Object>>();
    }

    /** Folder mapped to the record by Box for Salesforce, or null. Read only: no DML. */
    public static String folderFor(Id recordId) {
        return new FolderMapping().forRecord(recordId);
    }

    /** Visible files and the upload folder, read with the parent token. */
    public static Workspace workspace(String folderId, String parentToken) {
        Workspace ws = new Workspace();
        ws.folderId = folderId;
        ws.uploadFolderId = folderId;
        List<Map<String, Object>> rootItems = items(folderId, parentToken);
        Set<String> visible = new Set<String>(PortalBoxSettings.VISIBLE_SUBFOLDERS);
        if (visible.isEmpty()) {
            addFiles(ws.files, rootItems, null);
        }
        for (Map<String, Object> item : rootItems) {
            if (item.get('type') != 'folder') continue;
            String name = (String) item.get('name');
            if (name == PortalBoxSettings.UPLOAD_SUBFOLDER) ws.uploadFolderId = (String) item.get('id');
            if (visible.contains(name)) addFiles(ws.files, items((String) item.get('id'), parentToken), name);
        }
        return ws;
    }

    /** The record folder and its direct subfolders: where signed files may land. */
    public static Set<String> folderTree(String folderId, String parentToken) {
        Set<String> ids = new Set<String>{ folderId };
        for (Map<String, Object> item : items(folderId, parentToken)) {
            if (item.get('type') == 'folder') ids.add((String) item.get('id'));
        }
        return ids;
    }

    public static Boolean containsFile(Workspace ws, String fileId) {
        for (Map<String, Object> file : ws.files) {
            if (file.get('id') == fileId) return true;
        }
        return false;
    }

    private static void addFiles(List<Map<String, Object>> target, List<Map<String, Object>> source, String folderName) {
        for (Map<String, Object> item : source) {
            if (item.get('type') != 'file') continue;
            target.add(new Map<String, Object>{
                'id' => item.get('id'), 'name' => item.get('name'), 'size' => item.get('size'),
                'modified_at' => item.get('modified_at'), 'folder' => folderName
            });
        }
    }

    private static List<Map<String, Object>> items(String folderId, String parentToken) {
        if (String.isBlank(folderId) || !folderId.isNumeric()) {
            throw new PortalBoxException('invalid_folder');
        }
        HttpResponse res = PortalBoxAuth.get('folders/' + folderId + '/items?limit=1000&fields=id,type,name,size,modified_at', parentToken);
        if (res.getStatusCode() != 200) {
            throw new PortalBoxException('box_list_failed');
        }
        List<Map<String, Object>> result = new List<Map<String, Object>>();
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
        for (Object entry : (List<Object>) body.get('entries')) {
            result.add((Map<String, Object>) entry);
        }
        return result;
    }

    public class PortalBoxException extends Exception {}

    /** Package mapping read after the caller's record access was checked. */
    private without sharing class FolderMapping {
        private String forRecord(Id recordId) {
            try {
                return new box.Toolkit().getFolderIdByRecordId(recordId);
            } catch (Exception e) {
                System.debug(LoggingLevel.WARN, 'Portal Box: folder lookup failed: ' + e.getMessage());
                return null;
            }
        }
    }
}
