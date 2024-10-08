<template>
  <LayoutHeader v-if="lead.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="lead.data._customActions"
        :actions="lead.data._customActions"
      />
      <component :is="lead.data._assignedTo?.length == 1 ? 'Button' : 'div'">
        <MultipleAvatar
          :avatars="lead.data._assignedTo"
          @click="showAssignmentModal = true"
        />
      </component>
    </template>
  </LayoutHeader>
  <div v-if="lead?.data" class="flex h-full overflow-hidden">
    <Tabs :key="route.params.doctype" v-model="tabIndex" v-slot="{ tab }" :tabs="tabs" class="overflow-x-scroll truncate">
      <DocActivities
        :key="tabIndex"
        ref="activities"
        :doctype="tab.doctype ?? route.params.doctype"
        :title="tab.label"
        :targetfield="tab.target_field ?? 'N/A'"
        :tabs="tabs"
        v-model:reload="reload"
        v-model:tabIndex="tabIndex"
        v-model="lead"
      />
    </Tabs>
    <Resizer class="flex flex-col justify-between border-l" side="right">
      <div
        class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium"
        @click="copyToClipboard(lead.data.name)"
      >
        {{ __(lead.data.name) }}
      </div>
      <FileUploader
        @success="(file) => updateField('image', file.file_url)"
        :validateFile="validateFile"
      >
        <template #default="{ openFileSelector, error }">
          <div class="flex items-center justify-start gap-5 border-b p-5">
            <div class="group relative size-12">
              <Avatar
                size="3xl"
                class="size-12"
                :label="lead.data.name || __('Untitled')"
                :image="lead.data.image"
              />
              <component
                :is="lead.data.image ? Dropdown : 'div'"
                v-bind="
                  lead.data.image
                    ? {
                        options: [
                          {
                            icon: 'upload',
                            label: lead.data.image
                              ? __('Change image')
                              : __('Upload image'),
                            onClick: openFileSelector,
                          },
                          {
                            icon: 'trash-2',
                            label: __('Remove image'),
                            onClick: () => updateField('image', ''),
                          },
                        ],
                      }
                    : { onClick: openFileSelector }
                "
                class="!absolute bottom-0 left-0 right-0"
              >
                <div
                  class="z-1 absolute bottom-0.5 left-0 right-0.5 flex h-9 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-3 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
                  style="
                    -webkit-clip-path: inset(12px 0 0 0);
                    clip-path: inset(12px 0 0 0);
                  "
                >
                  <CameraIcon class="size-4 cursor-pointer text-white" />
                </div>
              </component>
            </div>
            <div class="flex flex-col gap-2.5 truncate">
              <Tooltip :text="lead.data.lead_name || __('Set first name')">
                <div class="truncate text-2xl font-medium">
                  {{ lead.data.name || __('Untitled') }}
                </div>
              </Tooltip>
              <div class="flex gap-1.5">
                <Tooltip v-if="callEnabled" :text="__('Make a call')">
                  <Button
                    class="h-7 w-7"
                    @click="
                      () =>
                        lead.data.mobile_no
                          ? makeCall(lead.data.mobile_no)
                          : errorMessage(__('No phone number set'))
                    "
                  >
                    <PhoneIcon class="h-4 w-4" />
                  </Button>
                </Tooltip>
                <Tooltip :text="__('Send an email')">
                  <Button class="h-7 w-7">
                    <Email2Icon
                      class="h-4 w-4"
                      @click="
                        lead.data.email
                          ? openEmailBox()
                          : errorMessage(__('No email set'))
                      "
                    />
                  </Button>
                </Tooltip>
                <Tooltip :text="__('Go to website')">
                  <Button class="h-7 w-7">
                    <LinkIcon
                      class="h-4 w-4"
                      @click="
                        lead.data.website
                          ? openWebsite(lead.data.website)
                          : errorMessage(__('No website set'))
                      "
                    />
                  </Button>
                </Tooltip>
              </div>
              <ErrorMessage :message="__(error)" />
            </div>
          </div>
        </template>
      </FileUploader>
      <div
        v-if="fieldsLayout.data.length"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <div class="flex flex-col overflow-y-auto">
          <div
            v-for="(section, i) in fieldsLayout.data"
            :key="section.label"
            class="flex flex-col p-3"
            :class="{ 'border-b': i !== fieldsLayout.data.length - 1 }"
          >
            <Section :is-opened="section.opened" :label="section.label">
              <SectionFields
                :key="lead.data.name"
                :fields="section.fields"
                v-model="lead.data"
                @update="updateField"
              />
              <template v-if="i == 0 && isManager()" #actions>
                <Button
                  variant="ghost"
                  class="w-7 mr-2"
                  @click="showSidePanelModal = true"
                >
                  <EditIcon class="h-4 w-4" />
                </Button>
              </template>
            </Section>
          </div>
        </div>
      </div>
      <div v-else class="flex flex-1 flex-col justify-between overflow-hidden my-2">
        <Section :is-opened="false" label="Add Layout">
          <template v-if="isManager()" #actions>
            <Button
              variant="ghost"
              class="w-7 mr-2"
              @click="showSidePanelModal = true"
            >
              <EditIcon class="h-4 w-4" />
            </Button>
          </template>
        </Section>
      </div>
    </Resizer>
  </div>
  <AssignmentModal
    v-if="showAssignmentModal"
    v-model="showAssignmentModal"
    v-model:assignees="lead.data._assignedTo"
    :doc="lead.data"
    :doctype="route.params.doctype"
  />
  <DocSidePanelModal v-if="showSidePanelModal" v-model="showSidePanelModal" />
</template>
<script setup>
import Resizer from '@/components/Resizer.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import DotIcon from '@/components/Icons/DotIcon.vue'
import LinkIcon from '@/components/Icons/LinkIcon.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import DocActivities from '@/components/Activities/DocActivities.vue'
import AssignmentModal from '@/components/Modals/AssignmentModal.vue'
import DocSidePanelModal from '@/components/Settings/DocSidePanelModal.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import Section from '@/components/Section.vue'
import SectionFields from '@/components/SectionFields.vue'
import SLASection from '@/components/SLASection.vue'
import CustomActions from '@/components/CustomActions.vue'
import {
  openWebsite,
  createToast,
  setupAssignees,
  setupCustomActions,
  errorMessage,
  copyToClipboard,
} from '@/utils'
import { globalStore } from '@/stores/global'
import { contactsStore } from '@/stores/contacts'
import { organizationsStore } from '@/stores/organizations'
import { statusesStore } from '@/stores/statuses'
import { usersStore } from '@/stores/users'
import { whatsappEnabled, callEnabled } from '@/composables/settings'
import {
  createResource,
  FileUploader,
  Dropdown,
  Tooltip,
  Avatar,
  Tabs,
  Switch,
  Breadcrumbs,
  call,
} from 'frappe-ui'
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const { $dialog, makeCall } = globalStore()
const { getContactByName, contacts } = contactsStore()
const { organizations } = organizationsStore()
const { statusOptions, getLeadStatus } = statusesStore()
const { isManager } = usersStore()
const route = useRoute()
const router = useRouter()

const props = defineProps({
  leadId: {
    type: String,
    required: true,
  },
})

const lead = createResource({
  url: 'crm.api.get_doc.get_doc',
  params: { doctype:route.params.doctype,name: route.params.docId },
  onSuccess: (data) => {
    setupAssignees(data)
    setupCustomActions(data, {
      doc: data,
      $dialog,
      router,
      updateField,
      createToast,
      deleteDoc: deleteLead,
      call,
    })
  },
})
const dynamicTabs = ref([]); // Dynamic tabs
const tabIndex = ref(0)
const tabs = computed(() => {
  let tabOptions = ref([
    {
      name: 'Activity',
      label: __('Activity'),
      icon: ActivityIcon,
      static: true
    },
    {
      name: 'Emails',
      label: __('Emails'),
      icon: EmailIcon,
      static: true
    },
    {
      name: 'Comments',
      label: __('Comments'),
      icon: CommentIcon,
      static: true
    },
    {
      name: 'Calls',
      label: __('Calls'),
      icon: PhoneIcon,
      condition: () => callEnabled.value,
      static: true
    },
    {
      name: 'Tasks',
      label: __('Tasks'),
      icon: TaskIcon,
      static: true
    },
    {
      name: 'Notes',
      label: __('Notes'),
      icon: NoteIcon,
      static: true
    },
    {
      name: 'WhatsApp',
      label: __('WhatsApp'),
      icon: WhatsAppIcon,
      condition: () => whatsappEnabled.value,
      static: true
    },
  ])
  return [...tabOptions.value.filter((tab) => (tab.condition ? tab.condition() : true)), ...dynamicTabs.value]
})

watch(() => [route.params.doctype,route.params.docId], async ([newdocType,newdocId]) => {
  if (!newdocType || !newdocId) return; // Check if the newVal exists
  tabIndex.value = 0;
  lead.params = {
    doctype: newdocType,
    name: newdocId
  };
  dynamicTabs.value = [];
  let additional_tabs = await call('crm.api.list.get_tabs', {
    name: newdocType,
  });
  if (additional_tabs.length) {
    additional_tabs.forEach((tab) => {
      dynamicTabs.value.push({
        name: tab.name,
        label: tab.label || (tab.linked_document || tab.parent_document) || 'Untitled',
        icon: DotIcon,
        doctype: tab.linked_document || tab.parent_document || newVal,
        target_field: tab.target_field || 'N/A',
      });
    });
  }
  lead.fetch();
}, { immediate: true, deep: true });

const reload = ref(false)
const showAssignmentModal = ref(false)
const showSidePanelModal = ref(false)

function updateLead(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  if (!Array.isArray(fieldname) && validateRequired(fieldname, value)) return

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: route.params.doctype,
      name: route.params.docId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      lead.reload()
      reload.value = true
      createToast({
        title: __('Doc updated'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      callback?.()
    },
    onError: (err) => {
      createToast({
        title: __('Error updating doc'),
        text: __(err.messages?.[0]),
        icon: 'x',
        iconClasses: 'text-red-600',
      })
    },
  })
}

function validateRequired(fieldname, value) {
  let meta = lead.data.fields_meta || {}
  if (meta[fieldname]?.reqd && !value) {
    createToast({
      title: __('Error Updating Lead'),
      text: __('{0} is a required field', [meta[fieldname].label]),
      icon: 'x',
      iconClasses: 'text-red-600',
    })
    return true
  }
  return false
}

const breadcrumbs = computed(() => {
  let items = [{ label: __(route.params.doctype), route: { name: 'Doctype' ,params: { doctype:route.params.doctype,viewType:"list" }} }]
  items.push({
    label: lead.data.name || __('Untitled'),
    route: { name: 'Doc', params: { doctype:route.params.doctype,docId: lead.data.name }},
  })
  return items
})




watch(tabs, (value) => {
  if (value && route.params.tabName) {
    let index = value.findIndex(
      (tab) => tab.name.toLowerCase() === route.params.tabName.toLowerCase(),
    )
    if (index !== -1) {
      tabIndex.value = index
    }
  }
})

function validateFile(file) {
  let extn = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg', 'jpeg'].includes(extn)) {
    return __('Only PNG and JPG images are allowed')
  }
}

const fieldsLayout = createResource({
  url: 'crm.api.doc.get_sidebar_fields',
  // cache: ['fieldsLayout', props.leadId],
  params: { doctype: route.params.doctype, name: route.params.docId },
  auto: true,
})

function updateField(name, value, callback) {
  updateLead(name, value, () => {
    lead.data[name] = value
    callback?.()
  })
}

async function deleteLead(name) {
  await call('frappe.client.delete', {
    doctype: route.params.doctype,
    name,
  })
  router.push({ name: 'Leads' })
}

// Convert to Deal
const showConvertToDealModal = ref(false)
const existingContactChecked = ref(false)
const existingOrganizationChecked = ref(false)

const existingContact = ref('')
const existingOrganization = ref('')

async function convertToDeal(updated) {
  let valueUpdated = false

  if (existingContactChecked.value && !existingContact.value) {
    createToast({
      title: __('Error'),
      text: __('Please select an existing contact'),
      icon: 'x',
      iconClasses: 'text-red-600',
    })
    return
  }

  // if (existingOrganizationChecked.value && !existingOrganization.value) {
  //   createToast({
  //     title: __('Error'),
  //     text: __('Please select an existing organization'),
  //     icon: 'x',
  //     iconClasses: 'text-red-600',
  //   })
  //   return
  // }

  // if (existingContactChecked.value && existingContact.value) {
  //   lead.data.salutation = getContactByName(existingContact.value).salutation
  //   lead.data.first_name = getContactByName(existingContact.value).first_name
  //   lead.data.last_name = getContactByName(existingContact.value).last_name
  //   lead.data.email_id = getContactByName(existingContact.value).email_id
  //   lead.data.mobile_no = getContactByName(existingContact.value).mobile_no
  //   existingContactChecked.value = false
  //   valueUpdated = true
  // }

  // if (existingOrganizationChecked.value && existingOrganization.value) {
  //   lead.data.organization = existingOrganization.value
  //   existingOrganizationChecked.value = false
  //   valueUpdated = true
  // }

  // if (valueUpdated) {
  //   updateLead(
  //     {
  //       salutation: lead.data.salutation,
  //       first_name: lead.data.first_name,
  //       last_name: lead.data.last_name,
  //       email_id: lead.data.email_id,
  //       mobile_no: lead.data.mobile_no,
  //       organization: lead.data.organization,
  //     },
  //     '',
  //     () => convertToDeal(true),
  //   )
  //   showConvertToDealModal.value = false
  // } else {
    // let deal = await call(
    //   'crm.fcrm.doctype.crm_lead.crm_lead.convert_to_deal',
    //   {
    //     lead: lead.data.name,
    //   },
    // )
    // if (deal) {
    //   if (updated) {
    //     await organizations.reload()
    //     await contacts.reload()
    //   }
    //   router.push({ name: 'Deal', params: { dealId: deal } })
    // }
  // }
}

const activities = ref(null)

function openEmailBox() {
  activities.value.emailBox.show = true
}
</script>