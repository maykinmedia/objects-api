import React, { useState } from "react";

import { CheckboxInput, TextInput, SelectInput } from "../../forms/inputs";
import { authFields } from "./auth-fields";


const PermissionForm = ({objectFields, dataFieldChoices, tokenChoices, objecttypeChoices, modeChoices, formData}) => {


    const {values, errors} = formData;
    const [mode, setMode]  = useState(values["mode"]);
    const [useFields, setUseFields] = useState(values["use_fields"]);
    const [fields, setFields] = useState(values["fields"] ? values["fields"].split(",") : []);
    const [dataFields, setDataFields] = useState(dataFieldChoices[values["object_type"]]);

    return (
     <fieldset className="module aligned">
        <div className="form-row">
            <SelectInput
                name="token_auth"
                id="id_token_auth"
                label="Token auth:"
                choices={tokenChoices}
                initialValue={values["token_auth"]}
                errors={errors["token_auth"]}
            />
        </div>

        <div className="form-row">
            <SelectInput
                name="object_type"
                id="id_object_type"
                label="Object type:"
                choices={objecttypeChoices}
                initialValue={values["object_type"]}
                errors={errors["object_type"]}
                onChange={(value) => {
                    setDataFields(dataFieldChoices[value]);
                    // remove other data fields from selected
                    const newFields = fields.filter(x => !x.startsWith("record__data__"))
                    setFields(newFields);
                }}
            />
        </div>

        <div className="form-row">
            <SelectInput
                name="mode"
                id="id_mode"
                label="Mode:"
                choices={modeChoices}
                initialValue={mode}
                errors={errors["mode"]}
                onChange={(value) => {
                    setMode(value);
                    if (value === "read_and_write") {
                        setUseFields(false);
                    }
                }}
            />

        </div>

        <div className="form-row">
            <CheckboxInput
                name="use_fields"
                id="id_use_fields"
                label="Use field-based authorization"
                disabled={mode === "read_and_write"}
                value={useFields}
                onChange={(value) => {setUseFields(value)}}
            />
        </div>

        <TextInput
                name="fields"
                id="id_fields"
                hidden={true}
                value={useFields ? fields : ""}
        />

        { useFields ?

            <div className="form-row">
                <label htmlFor="id_selected_fields">Fields:</label>
                <div id="id_selected_fields" className="permission-fields">
                    { authFields(objectFields, dataFields, fields, setFields) }
                </div>
            </div>

            : null
        }

     </fieldset>
    );
};


export { PermissionForm };
