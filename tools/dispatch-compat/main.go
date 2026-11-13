// Optional compatibility probe. Run through scripts/check_dispatch.py.
package main

import (
	"archive/zip"
	"bytes"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"github.com/unofficialbox/box-dispatch/internal/bcl"
	"github.com/unofficialbox/box-dispatch/internal/lifecycle"
	"github.com/unofficialbox/box-dispatch/internal/salesforceapi"
	"github.com/unofficialbox/box-dispatch/internal/solution"
	"github.com/unofficialbox/box-dispatch/internal/workspace"
	"io"
	"os"
	"path/filepath"
)

func main() {
	if err := check(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
func check() error {
	root, destination := os.Args[1], os.Args[2]
	manifest, err := solution.Load(root)
	if err != nil {
		return err
	}
	if manifest.TemplateID != "dispatch-smoke" {
		return fmt.Errorf("generated scenario identity was not refreshed")
	}
	if _, err := workspace.Build(workspace.PackageRequest{Repository: root, Destination: destination, TemplateID: manifest.TemplateID, Components: []string{"box", "salesforce"}}); err != nil {
		return err
	}
	box, err := lifecycle.PlanProvider(destination, "box")
	if err != nil {
		return err
	}
	if len(box.Planned) < 5 {
		return fmt.Errorf("Box plan is incomplete: %#v", box.Planned)
	}
	sf, err := lifecycle.PlanProvider(destination, "salesforce")
	if err != nil {
		return err
	}
	if len(sf.Planned) < 7 {
		return fmt.Errorf("Salesforce plan is incomplete: %#v", sf.Planned)
	}
	if _, err := bcl.ConfigObject(filepath.Join(destination, "config", "box", "metadata-templates.bcl")); err != nil {
		return err
	}
	project := filepath.Join(destination, "salesforce-project")
	inventory, _, err := salesforceapi.InventorySource(project)
	if err != nil {
		return err
	}
	selected := []string{}
	for component := range inventory {
		selected = append(selected, component)
	}
	data, _, err := salesforceapi.BuildMetadataPackage(project, selected)
	if err != nil {
		return err
	}
	archive, err := zip.NewReader(bytes.NewReader(data), int64(len(data)))
	if err != nil {
		return err
	}
	hasManifest, fields := false, 0
	for _, file := range archive.File {
		if file.Name == "package.xml" {
			hasManifest = true
		}
		if filepath.Ext(file.Name) != ".object" {
			continue
		}
		reader, err := file.Open()
		if err != nil {
			return err
		}
		raw, err := io.ReadAll(reader)
		reader.Close()
		if err != nil {
			return err
		}
		var object struct {
			Fields []struct {
				Name string `xml:"fullName"`
			} `xml:"fields"`
		}
		if err := xml.Unmarshal(raw, &object); err != nil {
			return err
		}
		fields += len(object.Fields)
	}
	if !hasManifest || fields < 6 {
		return fmt.Errorf("metadata archive is incomplete: package.xml=%v fields=%d", hasManifest, fields)
	}
	return json.NewEncoder(os.Stdout).Encode(map[string]any{"dispatch_package_clone": "passed", "manifest_loader": "passed", "box_planned": box.Planned, "salesforce_planned": sf.Planned, "salesforce_zip_fields": fields, "provider_calls": 0})
}
