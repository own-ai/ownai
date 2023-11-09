<template>
  <Workshop
    :items="aiStore.ais"
    :selected-item-id="selectedAiId"
    @select-item="selectAi"
  >
    <template v-slot:offcanvas-toggle-label>Select AI</template>
    <template v-slot:offcanvas-header>
      <NewAiDropdown @load="loadFile" @create="newEmpty" />
    </template>
    <template v-slot:actionbar>
      <input
        type="file"
        ref="fileInputRef"
        class="d-none"
        accept=".aifile"
        @change="changeInputFile"
      />
      <NewAiDropdown
        class="mx-2 d-none d-lg-block"
        @load="loadFile"
        @create="newEmpty"
      />
      <button
        v-if="isDirty"
        type="button"
        class="btn btn-primary mx-2"
        @click="save"
      >
        Save
      </button>
      <div v-else class="text-secondary mx-2">Saved</div>
    </template>
    <template v-slot:list-item-dropdown-items="props">
      <li>
        <a
          class="dropdown-item"
          href="#"
          @click.prevent.stop="duplicate(props.item.id)"
        >
          Duplicate
        </a>
      </li>
      <li>
        <a
          class="dropdown-item dropdown-item-danger"
          href="#"
          @click.prevent.stop="deleteAi(props.item.id)"
        >
          Delete
        </a>
      </li>
    </template>
    <template v-slot:list-empty>
      No AI set up yet.
      <NewAiDropdown class="m-3" @load="loadFile" @create="newEmpty" />
    </template>
    <div ref="codemirrorRef" class="overflow-auto w-100"></div>
  </Workshop>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useRoute, useRouter, onBeforeRouteUpdate } from "vue-router";
import { useAiStore } from "@/store/ai";
import { basicSetup } from "codemirror";
import { json, jsonParseLinter } from "@codemirror/lang-json";
import { linter, lintGutter } from "@codemirror/lint";
import { EditorState } from "@codemirror/state";
import { EditorView, ViewUpdate } from "@codemirror/view";
import { indentationMarkers } from "@replit/codemirror-indentation-markers";
import Workshop from "./Workshop.vue";
import NewAiDropdown from "./ai/NewAiDropdown.vue";
import type { Ai } from "@/types/Ai";
import type { Aifile } from "@/types/Aifile";
import type { IdName } from "@/types/IdName";
import type { Optional } from "@/types/Optional";

const aiStore = useAiStore();

const isDirty = ref<boolean>(false);
const isInitialChange = ref<boolean>(true);

const fileInputRef = ref();

const codemirrorRef = ref();
let codemirrorView: EditorView;

const route = useRoute();
const router = useRouter();

const selectedAiId = ref<number | null>();

const aiToJson = (ai: Ai | undefined) => {
  if (!ai) {
    return "";
  }
  const aifile: Aifile = {
    name: ai.name,
    aifileversion: 1,
    chain: ai.chain,
  };
  if (ai.input_labels) {
    aifile["input_labels"] = ai.input_labels;
  }
  if (ai.greeting) {
    aifile["greeting"] = ai.greeting;
  }
  return JSON.stringify(aifile, null, 2);
};

const jsonToAi = (id: number | undefined, jsonString: string) => {
  const inputKeys = new Set<string>();
  const reviver = function (this: any, key: string, value: any) {
    if (
      key === "input_key" &&
      typeof value === "string" &&
      value.startsWith("input_")
    ) {
      inputKeys.add(value);
    }
    if (key === "input_variables" && value?.[Symbol.iterator]) {
      for (const inputVariable of value) {
        if (
          typeof inputVariable === "string" &&
          inputVariable.startsWith("input_")
        ) {
          inputKeys.add(inputVariable);
        }
      }
    }
    return value;
  };
  const json = JSON.parse(jsonString, reviver);
  const ai: Optional<Ai, "id"> = {
    name: json["name"],
    input_keys: Array.from(inputKeys),
    chain: json["chain"],
  };
  if (json["input_labels"]) {
    ai.input_labels = json["input_labels"];
  }
  if (json["greeting"]) {
    ai.greeting = json["greeting"];
  }
  if (id !== undefined) {
    ai.id = id;
  }
  return ai;
};

const shouldDiscardUnsavedChanges = () => {
  if (!isDirty.value) {
    return true;
  }
  return confirm("Unsaved changes will be lost. Really discard your changes?");
};

const selectAi = (ai: IdName) => {
  if (!shouldDiscardUnsavedChanges()) {
    return;
  }
  selectedAiId.value = ai.id;
  router.push({ params: { id: ai.id } });
};

const save = async () => {
  try {
    const json = jsonToAi(
      selectedAiId.value || undefined,
      codemirrorView.state.doc.toString(),
    );
    if (json.id !== undefined) {
      await aiStore.updateAi({ ...json, id: json.id });
    } else {
      await aiStore.createAi(json);
    }
    isDirty.value = false;
  } catch (error) {
    if (error instanceof SyntaxError) {
      alert(
        "Cannot save the AI because its code is invalid. Please fix the code and try again.\n\nError message: " +
          error.message,
      );
    } else {
      alert(error);
    }
  }
};

const open = (newDoc: string) => {
  isInitialChange.value = true;
  isDirty.value = false;
  codemirrorView?.dispatch({
    changes: { from: 0, to: codemirrorView?.state.doc.length, insert: newDoc },
  });
};

const newEmpty = () => {
  if (!shouldDiscardUnsavedChanges()) {
    return;
  }
  selectedAiId.value = null;
  router.push({ params: { id: "new" } });
  open("");
  isDirty.value = true;
};

const duplicate = async (aiId: number) => {
  const ai = aiStore.ais.find((ai) => ai.id === aiId);
  if (!ai || !shouldDiscardUnsavedChanges()) {
    return;
  }
  const { id, ...aiCopy } = { ...ai, name: `${ai.name} copy` };
  try {
    const newAi = await aiStore.createAi(aiCopy);
    selectedAiId.value = newAi.id;
    router.push({ params: { id: newAi.id } });
  } catch (error) {
    alert(error);
  }
};

const deleteAi = async (aiId: number) => {
  const ai = aiStore.ais.find((ai) => ai.id === aiId);
  if (ai && confirm(`Really delete ${ai.name}?`)) {
    try {
      await aiStore.deleteAi(ai.id);
      if (ai.id === selectedAiId.value) {
        newEmpty();
      }
    } catch (error) {
      alert(error);
    }
  }
};

const loadFile = () => {
  fileInputRef.value.click();
};

const changeInputFile = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (!input.files?.length) {
    return;
  }

  const file = input.files[0];
  const reader = new FileReader();

  reader.onload = async (e) => {
    const text = e.target?.result;
    if (typeof text === "string") {
      const json = jsonToAi(undefined, text);
      const newAi = await aiStore.createAi(json);
      selectedAiId.value = newAi.id;
      router.push({ params: { id: newAi.id } });
    }
  };

  reader.readAsText(file);
};

onMounted(async () => {
  await aiStore.fetchAis();

  const paramId = route.params.id;
  let doc: string;
  if (paramId === "new" || !aiStore.ais?.length) {
    selectedAiId.value = null;
    doc = "";
  } else if (typeof paramId === "string" && !isNaN(parseInt(paramId))) {
    selectedAiId.value = parseInt(paramId);
    doc = aiToJson(aiStore.ais.find((ai) => ai.id === selectedAiId.value));
  } else {
    selectedAiId.value = aiStore.ais[0].id;
    router.push({ params: { id: aiStore.ais[0].id } });
    doc = aiToJson(aiStore.ais[0]);
  }

  codemirrorView = new EditorView({
    state: EditorState.create({
      doc,
      extensions: [
        basicSetup,
        json(),
        linter(jsonParseLinter()),
        lintGutter(),
        indentationMarkers(),
        EditorView.updateListener.of((update: ViewUpdate) => {
          if (update.docChanged) {
            if (isInitialChange.value) {
              isInitialChange.value = false;
            } else {
              isDirty.value = true;
            }
          }
        }),
      ],
    }),
    parent: codemirrorRef.value,
  });

  addEventListener("beforeunload", function (event) {
    if (isDirty.value) {
      const confirmationMessage =
        "Unsaved changes will be lost. Really discard your changes?";
      event.returnValue = confirmationMessage;
      return confirmationMessage;
    }
  });
});

watch(selectedAiId, (newAiId) => {
  if (newAiId) {
    open(aiToJson(aiStore.ais.find((ai) => ai.id === newAiId)));
  }
});

onBeforeRouteUpdate((to, from) => {
  if (to.params.id !== from.params.id) {
    if (to.params.id === "new") {
      if (selectedAiId.value !== null) {
        if (!shouldDiscardUnsavedChanges()) {
          return false;
        }
        selectedAiId.value = null;
        open("");
      }
    } else if (
      typeof to.params.id === "string" &&
      !isNaN(parseInt(to.params.id))
    ) {
      const id = parseInt(to.params.id);
      if (selectedAiId.value !== id) {
        if (!shouldDiscardUnsavedChanges()) {
          return false;
        }
        selectedAiId.value = id;
        open(aiToJson(aiStore.ais.find((ai) => ai.id === id)));
      }
    }
  }
});
</script>

<style>
.cm-editor {
  height: 100%;
}
</style>
