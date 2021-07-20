<div className="form-row field-token_auth">


    <div>


        <label className="required" htmlFor="id_token_auth">Token auth:</label>

        <div className="related-widget-wrapper">
            <select name="token_auth" required="" id="id_token_auth">
                <option value="">---------</option>

                <option value="33185022d61a2fd23f6bae2dc7216a21c6ccc3d3" selected="">Anna Shamray</option>

            </select>

            <a className="related-widget-wrapper-link change-related" id="change_id_token_auth"
               data-href-template="/admin/token/tokenauth/__fk__/change/?_to_field=token&amp;_popup=1"
               title="Change selected token authorization"
               href="/admin/token/tokenauth/33185022d61a2fd23f6bae2dc7216a21c6ccc3d3/change/?_to_field=token&amp;_popup=1"><img
                src="/static/admin/img/icon-changelink.svg" alt="Change"></a><a
            className="related-widget-wrapper-link add-related" id="add_id_token_auth"
            href="/admin/token/tokenauth/add/?_to_field=token&amp;_popup=1" title="Add another token authorization"><img
            src="/static/admin/img/icon-addlink.svg" alt="Add"></a>

        </div>


    </div>

</div>

<div className="form-row field-object_type">


    <div>


        <label className="required" htmlFor="id_object_type">Object type:</label>

        <div className="related-widget-wrapper">
            <select name="object_type" required="" id="id_object_type">
                <option value="">---------</option>

                <option value="2" selected="">Objecttypen API: Straatverlichting</option>

                <option value="3">Objecttypen API: Melding</option>

                <option value="1">Objecttypen API: Boom</option>

                <option value="4">Objecttypen API: boom</option>

            </select>

            <a className="related-widget-wrapper-link change-related" id="change_id_object_type"
               data-href-template="/admin/core/objecttype/__fk__/change/?_to_field=id&amp;_popup=1"
               title="Change selected object type"
               href="/admin/core/objecttype/2/change/?_to_field=id&amp;_popup=1"><img
                src="/static/admin/img/icon-changelink.svg" alt="Change"></a><a
            className="related-widget-wrapper-link add-related" id="add_id_object_type"
            href="/admin/core/objecttype/add/?_to_field=id&amp;_popup=1" title="Add another object type"><img
            src="/static/admin/img/icon-addlink.svg" alt="Add"></a>

        </div>


    </div>

</div>

<div className="form-row field-mode">


    <div>


        <label className="required" htmlFor="id_mode">Mode:</label>

        <select name="mode" required="" id="id_mode">
            <option value="">---------</option>

            <option value="read_only">Read-only</option>

            <option value="read_and_write" selected="">Read and write</option>

        </select>


        <div className="help">Permission mode</div>

    </div>

</div>

<div className="form-row field-use_fields">


    <div className="checkbox-row">


        <input type="checkbox" name="use_fields" id="id_use_fields"><label className="vCheckboxLabel"
                                                                           htmlFor="id_use_fields">Use fields</label>


            <div className="help">Use field-based authorization</div>

    </div>

</div>

<div className="form-row field-fields">


    <div>


        <label htmlFor="id_fields">Fields:</label>

        <input type="text" name="fields" id="id_fields"><input type="hidden" name="initial-fields"
                                                               id="initial-id_fields">


            <div className="help">Fields allowed for this token. Supports only first level of the `record.data`
                properties
            </div>

    </div>

</div>

