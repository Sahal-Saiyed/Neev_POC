import streamlit as st

from formula_utils import (
    calculate_ld,
    parse_bar_dia,
    calculate_shape_outputs,
    CONCRETE_GRADE_VALUES,
    STEEL_GRADE_VALUES
)

from services.beam_service import (
    create_beam,
    list_beams,
    get_beam_by_id,
    update_beam_calculation
)

from services.shape_service import (
    list_available_shapes_for_project,
    resolve_project_shape
)

from ui.common import (
    get_selected_autocad_import,
    render_shape_image
)

def beam_tab(project, import_item):
    st.markdown("### Beam")

    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])

    with header_col1:
        search_text = st.text_input(
            "Search Beam",
            label_visibility="collapsed",
            placeholder="Search Here"
        )

    with header_col2:
        status_filter = st.selectbox(
            "Beam Status",
            ["All", "Filled", "Unfilled"],
            label_visibility="collapsed"
        )

    with header_col3:
        if st.button("+ Add Beam", use_container_width=True):
            st.session_state.show_new_beam_form = True
            st.rerun()

    if st.session_state.show_new_beam_form:
        new_beam_form(project, import_item)

    st.markdown("---")

    show_beams(project, import_item, search_text, status_filter)


def new_beam_form(project, import_item):
    st.subheader("Add Beam")

    with st.form("new_beam_form"):
        beam_name = st.text_input("Beam Name")
        beam_description = st.text_area("Beam Description")

        col1, col2 = st.columns(2)

        with col1:
            save = st.form_submit_button("Save")

        with col2:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state.show_new_beam_form = False
        st.rerun()

    if save:
        beam_name = beam_name.strip()
        beam_description = beam_description.strip()

        if not beam_name:
            st.error("Beam name is required.")
            return

        beam_id = create_beam(
            project_id=str(project["_id"]),
            autocad_import_id=str(import_item["_id"]),
            block_id=import_item.get("block_id"),
            block_name=import_item.get("block_name"),
            floor_id=import_item.get("floor_id"),
            floor_name=import_item.get("floor_name"),
            beam_name=beam_name,
            beam_description=beam_description,
            created_by=st.session_state.email,
            created_by_name=st.session_state.name
        )

        st.session_state.selected_beam_id = beam_id
        st.session_state.project_subpage = "beam_detail"
        st.session_state.show_new_beam_form = False

        st.success("Beam created successfully.")
        st.rerun()


def show_beams(project, import_item, search_text="", status_filter="All"):
    beams = list_beams(
        project_id=str(project["_id"]),
        autocad_import_id=str(import_item["_id"]),
        search_text=search_text,
        status_filter=status_filter
    )

    if not beams:
        st.info("No beams found.")
        return

    for beam in beams:
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            if st.button(
                beam.get("beam_name", "Untitled Beam"),
                key=f"open_beam_{beam['_id']}"
            ):
                st.session_state.selected_beam_id = str(beam["_id"])
                st.session_state.project_subpage = "beam_detail"
                st.rerun()

            if beam.get("beam_description"):
                st.caption(beam.get("beam_description"))

        with col2:
            if beam.get("status") == "Filled":
                st.success("Filled")
            else:
                st.warning("Unfilled")

        with col3:
            if st.button(
                "Open",
                key=f"open_beam_action_{beam['_id']}",
                use_container_width=True
            ):
                st.session_state.selected_beam_id = str(beam["_id"])
                st.session_state.project_subpage = "beam_detail"
                st.rerun()

        st.markdown("---")


def get_selected_beam():
    return get_beam_by_id(st.session_state.selected_beam_id)

def beam_detail_subpage(project):
    import_item = get_selected_autocad_import()
    beam = get_selected_beam()

    if not import_item:
        st.error("AutoCAD import not found.")

        if st.button("Back to AutoCAD Imports"):
            st.session_state.project_subpage = "autocad_import"
            st.session_state.selected_autocad_import_id = None
            st.session_state.selected_beam_id = None
            st.rerun()

        return

    if not beam:
        st.error("Beam not found.")

        if st.button("Back to Beams"):
            st.session_state.project_subpage = "autocad_import_detail"
            st.session_state.selected_beam_id = None
            st.rerun()

        return

    st.title(f"Beam › {beam.get('beam_name', 'Beam')}")
    st.caption(
        f"Home • {project.get('project_name', 'Project')} • "
        f"AutoCAD Import • {import_item.get('name', 'Import')} • Beam"
    )

    st.markdown("---")

    if st.button("⬅ Back to Beam List"):
        st.session_state.project_subpage = "autocad_import_detail"
        st.session_state.selected_beam_id = None
        st.rerun()

    st.markdown("---")

    beam_input_calculation_form(project, import_item, beam)

def beam_input_calculation_form(project, import_item, beam):
    project_id = str(project["_id"])

    available_shapes = list_available_shapes_for_project(
        project_id=project_id,
        category="beam"
    )

    if not available_shapes:
        st.error("No beam shapes found.")
        return

    shape_options = {
        item["option_label"]: item["option_key"]
        for item in available_shapes
    }

    existing_shape_key = beam.get("selected_shape_key")

    if not existing_shape_key:
        if beam.get("shape_source") == "custom" and beam.get("custom_shape_id"):
            existing_shape_key = f"custom:{beam.get('custom_shape_id')}"
        elif beam.get("shape_id"):
            existing_shape_key = f"global:{beam.get('shape_id')}"

    default_shape_index = 0

    for index, item in enumerate(available_shapes):
        if item["option_key"] == existing_shape_key:
            default_shape_index = index
            break

    selected_shape_label = st.selectbox(
        "Select Shape",
        list(shape_options.keys()),
        index=default_shape_index
    )

    selected_shape_key = shape_options[selected_shape_label]

    selected_shape = resolve_project_shape(
        project_id=project_id,
        selected_shape_key=selected_shape_key
    )

    if not selected_shape:
        st.error("Selected shape could not be resolved.")
        return

    selected_shape_name = selected_shape.get("shape_name")
    selected_shape_id = selected_shape.get("shape_id")

    st.markdown("#### Shape:")
    st.subheader(selected_shape.get("shape_name", "Shape"))

    image_path = selected_shape.get("image_path")
    image_file_id = selected_shape.get("image_file_id")

    render_shape_image(
        image_file_id=image_file_id,
        image_path=image_path,
        width=350,
        missing_message="No image available for this shape."
    )

    st.markdown("---")

    old_inputs = beam.get("inputs", {})

    with st.form("beam_input_calculation_form"):
        st.subheader("Beam Input Details")

        number_of_repetitions = st.number_input(
            "Number of Repetitions",
            min_value=1,
            value=int(old_inputs.get("number_of_repetitions", 1))
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            beam_length = st.number_input(
                "Beam Length BX (mm)",
                min_value=0.0,
                value=float(old_inputs.get("BX", 0.0))
            )

        with col2:
            beam_width = st.number_input(
                "Beam Width BY (mm)",
                min_value=0.0,
                value=float(old_inputs.get("BY", 0.0))
            )

        with col3:
            beam_depth = st.number_input(
                "Beam Depth BZ (mm)",
                min_value=0.0,
                value=float(old_inputs.get("BZ", 0.0))
            )

        col4, col5 = st.columns(2)

        with col4:
            column_left = st.number_input(
                "Column in Left CX (mm)",
                min_value=0.0,
                value=float(old_inputs.get("CX", 0.0))
            )

        with col5:
            column_right = st.number_input(
                "Column in Right CY (mm)",
                min_value=0.0,
                value=float(old_inputs.get("CY", 0.0))
            )

        bar_options = [
            "2-T12",
            "2-T16",
            "4-T20",
            "3-T16",
            "3-T20",
            "2-T20",
            "4-T25",
            "3-T12EF"
        ]

        old_bar_dia = old_inputs.get("bar_dia", "2-T12")
        bar_index = bar_options.index(old_bar_dia) if old_bar_dia in bar_options else 0

        bar_dia = st.selectbox(
            "Select Bar & Dia",
            bar_options,
            index=bar_index
        )

        cover = st.number_input(
            "Cover CO (mm)",
            min_value=0.0,
            value=float(old_inputs.get("CO", 25.0))
        )

        col6, col7 = st.columns(2)

        concrete_options = list(CONCRETE_GRADE_VALUES.keys())
        old_gc_label = old_inputs.get("grade_of_concrete_label", "M25")
        gc_index = concrete_options.index(old_gc_label) if old_gc_label in concrete_options else 1

        with col6:
            grade_of_concrete = st.selectbox(
                "Grade of Concrete",
                concrete_options,
                index=gc_index
            )

        steel_options = list(STEEL_GRADE_VALUES.keys())
        old_gs_label = old_inputs.get("grade_of_steel_label", "Fe500")
        gs_index = steel_options.index(old_gs_label) if old_gs_label in steel_options else 1

        with col7:
            grade_of_steel = st.selectbox(
                "Grade of Steel",
                steel_options,
                index=gs_index
            )

        calculate = st.form_submit_button("Calculate & Save")

    if calculate:
        if beam_length <= 0:
            st.error("Beam length is required.")
            return

        if beam_width <= 0:
            st.error("Beam width is required.")
            return

        if beam_depth <= 0:
            st.error("Beam depth is required.")
            return

        BR, D = parse_bar_dia(bar_dia)

        GC = CONCRETE_GRADE_VALUES[grade_of_concrete]
        GS = STEEL_GRADE_VALUES[grade_of_steel]
        LD = calculate_ld(grade_of_concrete, grade_of_steel, D)

        variables = {
            "number_of_repetitions": number_of_repetitions,
            "BX": beam_length,
            "BY": beam_width,
            "BZ": beam_depth,
            "CX": column_left,
            "CY": column_right,
            "CO": cover,
            "BR": BR,
            "D": D,
            "GC": GC,
            "GS": GS,
            "LD": LD,

            # hidden/default values for POC
            "SD": 8,
            "LS": 2,
            "SS": 150
        }

        outputs = calculate_shape_outputs(selected_shape, variables)

        beam_update = {
            "selected_shape_key": selected_shape_key,
            "shape_id": selected_shape_id,
            "shape_name": selected_shape_name,
            "shape_source": selected_shape.get("shape_source"),
            "base_shape_id": selected_shape.get("base_shape_id"),
            "custom_shape_id": selected_shape.get("custom_shape_id"),
            "inputs": {
                "number_of_repetitions": number_of_repetitions,
                "BX": beam_length,
                "BY": beam_width,
                "BZ": beam_depth,
                "CX": column_left,
                "CY": column_right,
                "CO": cover,
                "bar_dia": bar_dia,
                "BR": BR,
                "D": D,
                "grade_of_concrete_label": grade_of_concrete,
                "grade_of_steel_label": grade_of_steel,
                "GC": GC,
                "GS": GS,
                "LD": LD,
                "SD": 8,
                "LS": 2,
                "SS": 150
            },
            "outputs": outputs,
            "status": "Filled"
        }

        update_beam_calculation(
            beam_id=str(beam["_id"]),
            beam_update=beam_update
        )

        st.success("Beam details calculated and saved successfully.")
        st.rerun()

    current_outputs = beam.get("outputs", [])

    if current_outputs:
        st.markdown("---")
        st.subheader("Output")

        output_cols = st.columns(3)

        for index, output in enumerate(current_outputs):
            col = output_cols[index % 3]

            with col:
                if output.get("value") is None:
                    st.error(
                        f"{output.get('output_name')}: Error - {output.get('error')}"
                    )
                else:
                    with st.container(border=True):
                        st.metric(
                            output.get("output_name", "Output"),
                            f"{output.get('value')} {output.get('unit', 'm')}"
                        )

        with st.expander("Formula used"):
            for output in current_outputs:
                st.write(
                    f"**{output.get('output_name')}** "
                    f"({output.get('formula_source', 'global')}) = "
                    f"`{output.get('formula_used')}`"
                )

