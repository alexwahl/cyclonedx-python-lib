# encoding: utf-8

# This file is part of CycloneDX Python Lib
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) OWASP Foundation. All Rights Reserved.

import base64
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, TypeVar

from packageurl import PackageURL

from cyclonedx.model import (
    AttachedText,
    DataClassification,
    DataFlow,
    Encoding,
    ExternalReference,
    ExternalReferenceType,
    HashType,
    License,
    LicenseChoice,
    Note,
    NoteText,
    OrganizationalContact,
    OrganizationalEntity,
    Property,
    Tool,
    XsUri,
)
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import (
    Commit,
    Component,
    ComponentEvidence,
    ComponentScope,
    ComponentType,
    Copyright,
    Patch,
    PatchClassification,
    Pedigree,
    Swid,
)
from cyclonedx.model.issue import IssueClassification, IssueType, IssueTypeSource
from cyclonedx.model.release_note import ReleaseNotes
from cyclonedx.model.service import Service
from cyclonedx.model.vulnerability import (
    BomTarget,
    BomTargetVersionRange,
    ImpactAnalysisAffectedStatus,
    ImpactAnalysisJustification,
    ImpactAnalysisResponse,
    ImpactAnalysisState,
    Vulnerability,
    VulnerabilityAdvisory,
    VulnerabilityAnalysis,
    VulnerabilityCredits,
    VulnerabilityRating,
    VulnerabilityReference,
    VulnerabilityScoreSource,
    VulnerabilitySeverity,
    VulnerabilitySource,
)

MOCK_TIMESTAMP: datetime = datetime(2021, 12, 31, 10, 0, 0, 0).replace(tzinfo=timezone.utc)
MOCK_UUID_1 = 'be2c6502-7e9a-47db-9a66-e34f729810a3'
MOCK_UUID_2 = '17e3b199-dc0b-42ef-bfdd-1fa81a1e3eda'
MOCK_UUID_3 = '0b049d09-64c0-4490-a0f5-c84d9aacf857'
MOCK_UUID_4 = 'cd3e9c95-9d41-49e7-9924-8cf0465ae789'
MOCK_UUID_5 = 'bb5911d6-1a1d-41c9-b6e0-46e848d16655'
MOCK_UUID_6 = 'df70b5f1-8f53-47a4-be48-669ae78795e6'

TEST_UUIDS = [
    MOCK_UUID_1, MOCK_UUID_2, MOCK_UUID_3, MOCK_UUID_4, MOCK_UUID_5, MOCK_UUID_6
]


def get_bom_with_component_setuptools_basic() -> Bom:
    return Bom(components=[get_component_setuptools_simple()])


def get_bom_with_component_setuptools_with_cpe() -> Bom:
    component = get_component_setuptools_simple()
    component.cpe = 'cpe:2.3:a:python:setuptools:50.3.2:*:*:*:*:*:*:*'
    return Bom(components=[component])


def get_bom_with_component_setuptools_no_component_version() -> Bom:
    return Bom(components=[get_component_setuptools_simple_no_version()])


def get_bom_with_component_setuptools_with_release_notes() -> Bom:
    component = get_component_setuptools_simple()
    component.release_notes = get_release_notes()
    return Bom(components=[component])


def get_bom_with_dependencies_valid() -> Bom:
    c1 = get_component_setuptools_simple()
    c1.dependencies.update([
        get_component_toml_with_hashes_with_references().bom_ref
    ])
    return Bom(components=[
        c1,
        get_component_toml_with_hashes_with_references()
    ])


def get_bom_with_dependencies_invalid() -> Bom:
    c1 = get_component_setuptools_simple()
    c1.dependencies.update([
        get_component_toml_with_hashes_with_references().bom_ref
    ])
    return Bom(components=[
        c1
    ])


def get_bom_with_metadata_component_and_dependencies() -> Bom:
    bom = Bom(components=[get_component_toml_with_hashes_with_references()])
    bom.metadata.component = get_component_setuptools_simple()
    bom.metadata.component.dependencies.update([get_component_toml_with_hashes_with_references().bom_ref])
    return bom


def get_bom_with_component_setuptools_complete() -> Bom:
    component = get_component_setuptools_simple(bom_ref=MOCK_UUID_6)
    component.supplier = get_org_entity_1()
    component.publisher = 'CycloneDX'
    component.description = 'This component is awesome'
    component.scope = ComponentScope.REQUIRED
    component.copyright = 'Apache 2.0 baby!'
    component.cpe = 'cpe:2.3:a:python:setuptools:50.3.2:*:*:*:*:*:*:*'
    component.swid = get_swid_1()
    component.pedigree = get_pedigree_1()
    component.external_references.add(
        get_external_reference_1()
    )
    component.properties = get_properties_1()
    component.components.update([
        get_component_setuptools_simple(),
        get_component_toml_with_hashes_with_references()
    ])
    component.evidence = ComponentEvidence(copyright_=[Copyright(text='Commercial'), Copyright(text='Commercial 2')])
    component.release_notes = get_release_notes()
    return Bom(components=[component])


def get_bom_with_component_setuptools_with_vulnerability() -> Bom:
    bom = Bom()
    component = get_component_setuptools_simple()
    vulnerability = Vulnerability(
        bom_ref='my-vuln-ref-1', id='CVE-2018-7489', source=get_vulnerability_source_nvd(),
        references=[
            VulnerabilityReference(id='SOME-OTHER-ID', source=VulnerabilitySource(
                name='OSS Index', url=XsUri('https://ossindex.sonatype.org/component/pkg:pypi/setuptools')
            ))
        ],
        ratings=[
            VulnerabilityRating(
                source=get_vulnerability_source_nvd(), score=Decimal(9.8), severity=VulnerabilitySeverity.CRITICAL,
                method=VulnerabilityScoreSource.CVSS_V3,
                vector='AN/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', justification='Some justification'
            ),
            VulnerabilityRating(
                source=get_vulnerability_source_owasp(), score=Decimal(2.7), severity=VulnerabilitySeverity.LOW,
                method=VulnerabilityScoreSource.CVSS_V3,
                vector='AV:L/AC:H/PR:N/UI:R/S:C/C:L/I:N/A:N', justification='Some other justification'
            )
        ],
        cwes=[22, 33], description='A description here', detail='Some detail here',
        recommendation='Upgrade',
        advisories=[
            VulnerabilityAdvisory(url=XsUri('https://nvd.nist.gov/vuln/detail/CVE-2018-7489')),
            VulnerabilityAdvisory(url=XsUri('http://www.securitytracker.com/id/1040693'))
        ],
        created=datetime(year=2021, month=9, day=1, hour=10, minute=50, second=42, microsecond=51979,
                         tzinfo=timezone.utc),
        published=datetime(year=2021, month=9, day=2, hour=10, minute=50, second=42, microsecond=51979,
                           tzinfo=timezone.utc),
        updated=datetime(year=2021, month=9, day=3, hour=10, minute=50, second=42, microsecond=51979,
                         tzinfo=timezone.utc),
        credits=VulnerabilityCredits(
            organizations=[
                get_org_entity_1()
            ],
            individuals=[get_org_contact_2()]
        ),
        tools=[
            Tool(vendor='CycloneDX', name='cyclonedx-python-lib')
        ],
        analysis=VulnerabilityAnalysis(
            state=ImpactAnalysisState.EXPLOITABLE, justification=ImpactAnalysisJustification.REQUIRES_ENVIRONMENT,
            responses=[ImpactAnalysisResponse.CAN_NOT_FIX], detail='Some extra detail'
        ),
        affects_targets=[
            BomTarget(
                ref=component.purl.to_string() if component.purl else None,
                versions=[BomTargetVersionRange(
                    version_range='49.0.0 - 54.0.0', status=ImpactAnalysisAffectedStatus.AFFECTED
                )]
            )
        ],
        properties=get_properties_1()
    )
    component.add_vulnerability(vulnerability=vulnerability)
    bom.components.add(component)
    return bom


def get_bom_with_component_toml_1() -> Bom:
    return Bom(components=[get_component_toml_with_hashes_with_references()])


def get_bom_just_complete_metadata() -> Bom:
    bom = Bom()
    bom.metadata.authors = [get_org_contact_1(), get_org_contact_2()]
    bom.metadata.component = Component(
        name='cyclonedx-python-lib', version='1.0.0', component_type=ComponentType.LIBRARY
    )
    bom.metadata.manufacture = get_org_entity_1()
    bom.metadata.supplier = get_org_entity_2()
    bom.metadata.licenses = [LicenseChoice(license_=License(
        spdx_license_id='Apache-2.0', license_text=AttachedText(
            content='VGVzdCBjb250ZW50IC0gdGhpcyBpcyBub3QgdGhlIEFwYWNoZSAyLjAgbGljZW5zZSE=', encoding=Encoding.BASE_64
        ), license_url=XsUri('https://www.apache.org/licenses/LICENSE-2.0.txt')
    ))]
    bom.metadata.properties = get_properties_1()
    return bom


def get_bom_with_external_references() -> Bom:
    bom = Bom(external_references=[
        get_external_reference_1(), get_external_reference_2()
    ])
    return bom


def get_bom_with_services_simple() -> Bom:
    bom = Bom(services=[
        Service(name='my-first-service'),
        Service(name='my-second-service')
    ])
    bom.metadata.component = Component(
        name='cyclonedx-python-lib', version='1.0.0', component_type=ComponentType.LIBRARY
    )
    return bom


def get_bom_with_services_complex() -> Bom:
    bom = Bom(services=[
        Service(
            name='my-first-service', bom_ref='my-specific-bom-ref-for-my-first-service',
            provider=get_org_entity_1(), group='a-group', version='1.2.3',
            description='Description goes here', endpoints=[
                XsUri('/api/thing/1'),
                XsUri('/api/thing/2')
            ],
            authenticated=False, x_trust_boundary=True, data=[
                DataClassification(flow=DataFlow.OUTBOUND, classification='public')
            ],
            licenses=[
                LicenseChoice(license_expression='Commercial')
            ],
            external_references=[
                get_external_reference_1()
            ],
            properties=get_properties_1(),
            release_notes=get_release_notes()
        ),
        Service(name='my-second-service')
    ])
    bom.metadata.component = Component(
        name='cyclonedx-python-lib', version='1.0.0', component_type=ComponentType.LIBRARY
    )
    return bom


def get_bom_with_nested_services() -> Bom:
    bom = Bom(services=[
        Service(
            name='my-first-service', bom_ref='my-specific-bom-ref-for-my-first-service',
            provider=get_org_entity_1(), group='a-group', version='1.2.3',
            description='Description goes here', endpoints=[
                XsUri('/api/thing/1'),
                XsUri('/api/thing/2')
            ],
            authenticated=False, x_trust_boundary=True, data=[
                DataClassification(flow=DataFlow.OUTBOUND, classification='public')
            ],
            licenses=[
                LicenseChoice(license_expression='Commercial')
            ],
            external_references=[
                get_external_reference_1()
            ],
            properties=get_properties_1(),
            services=[
                Service(
                    name='first-nested-service'
                ),
                Service(
                    name='second-nested-service', bom_ref='my-specific-bom-ref-for-second-nested-service',
                    provider=get_org_entity_1(), group='no-group', version='3.2.1',
                    authenticated=True, x_trust_boundary=False,
                )
            ],
            release_notes=get_release_notes()
        ),
        Service(
            name='my-second-service',
            services=[
                Service(
                    name='yet-another-nested-service', provider=get_org_entity_1(), group='what-group', version='6.5.4'
                ),
                Service(
                    name='another-nested-service',
                    bom_ref='my-specific-bom-ref-for-another-nested-service',
                )
            ],
        )
    ])
    bom.metadata.component = Component(
        name='cyclonedx-python-lib', version='1.0.0', component_type=ComponentType.LIBRARY
    )
    return bom


def get_component_setuptools_simple(bom_ref: Optional[str] = None) -> Component:
    return Component(
        name='setuptools', version='50.3.2',
        bom_ref=bom_ref or 'pkg:pypi/setuptools@50.3.2?extension=tar.gz',
        purl=PackageURL(
            type='pypi', name='setuptools', version='50.3.2', qualifiers='extension=tar.gz'
        ),
        licenses=[LicenseChoice(license_expression='MIT License')],
        author='Test Author'
    )


def get_component_setuptools_simple_no_version(bom_ref: Optional[str] = None) -> Component:
    return Component(
        name='setuptools', bom_ref=bom_ref or 'pkg:pypi/setuptools?extension=tar.gz',
        purl=PackageURL(
            type='pypi', name='setuptools', qualifiers='extension=tar.gz'
        ),
        licenses=[LicenseChoice(license_expression='MIT License')],
        author='Test Author'
    )


def get_component_toml_with_hashes_with_references(bom_ref: Optional[str] = None) -> Component:
    return Component(
        name='toml', version='0.10.2', bom_ref=bom_ref or 'pkg:pypi/toml@0.10.2?extension=tar.gz',
        purl=PackageURL(
            type='pypi', name='toml', version='0.10.2', qualifiers='extension=tar.gz'
        ), hashes=[
            HashType.from_composite_str('sha256:806143ae5bfb6a3c6e736a764057db0e6a0e05e338b5630894a5f779cabb4f9b')
        ], external_references=[
            get_external_reference_1()
        ]
    )


def get_external_reference_1() -> ExternalReference:
    return ExternalReference(
        reference_type=ExternalReferenceType.DISTRIBUTION,
        url=XsUri('https://cyclonedx.org'),
        comment='No comment',
        hashes=[
            HashType.from_composite_str(
                'sha256:806143ae5bfb6a3c6e736a764057db0e6a0e05e338b5630894a5f779cabb4f9b')
        ]
    )


def get_external_reference_2() -> ExternalReference:
    return ExternalReference(
        reference_type=ExternalReferenceType.WEBSITE,
        url=XsUri('https://cyclonedx.org')
    )


def get_issue_1() -> IssueType:
    return IssueType(
        classification=IssueClassification.SECURITY, id_='CVE-2021-44228', name='Apache Log3Shell',
        description='Apache Log4j2 2.0-beta9 through 2.12.1 and 2.13.0 through 2.15.0 JNDI features...',
        source=IssueTypeSource(name='NVD', url=XsUri('https://nvd.nist.gov/vuln/detail/CVE-2021-44228')),
        references=[
            XsUri('https://logging.apache.org/log4j/2.x/security.html'),
            XsUri('https://central.sonatype.org/news/20211213_log4shell_help')
        ]
    )


def get_issue_2() -> IssueType:
    return IssueType(
        classification=IssueClassification.SECURITY, id_='CVE-2021-44229', name='Apache Log4Shell',
        description='Apache Log4j2 2.0-beta9 through 2.12.1 and 2.13.0 through 2.15.0 JNDI features...',
        source=IssueTypeSource(name='NVD', url=XsUri('https://nvd.nist.gov/vuln/detail/CVE-2021-44228')),
        references=[
            XsUri('https://logging.apache.org/log4j/2.x/security.html'),
            XsUri('https://central.sonatype.org/news/20211213_log4shell_help')
        ]
    )


def get_org_contact_1() -> OrganizationalContact:
    return OrganizationalContact(name='Paul Horton', email='paul.horton@owasp.org')


def get_org_contact_2() -> OrganizationalContact:
    return OrganizationalContact(name='A N Other', email='someone@somewhere.tld', phone='+44 (0)1234 567890')


def get_org_entity_1() -> OrganizationalEntity:
    return OrganizationalEntity(
        name='CycloneDX', urls=[XsUri('https://cyclonedx.org')], contacts=[get_org_contact_1(), get_org_contact_2()]
    )


def get_org_entity_2() -> OrganizationalEntity:
    return OrganizationalEntity(
        name='Cyclone DX', urls=[XsUri('https://cyclonedx.org/')], contacts=[get_org_contact_2()]
    )


def get_pedigree_1() -> Pedigree:
    return Pedigree(
        ancestors=[
            get_component_setuptools_simple(bom_ref='ccc8d7ee-4b9c-4750-aee0-a72585152291'),
            get_component_setuptools_simple_no_version(bom_ref='8a3893b3-9923-4adb-a1d3-47456636ba0a')
        ],
        descendants=[
            get_component_setuptools_simple_no_version(bom_ref='28b2d8ce-def0-446f-a221-58dee0b44acc'),
            get_component_toml_with_hashes_with_references(bom_ref='555ca729-93c6-48f3-956e-bdaa4a2f0bfa')
        ],
        variants=[
            get_component_toml_with_hashes_with_references(bom_ref='e7abdcca-5ba2-4f29-b2cf-b1e1ef788e66'),
            get_component_setuptools_simple(bom_ref='ded1d73e-1fca-4302-b520-f1bc53979958')
        ],
        commits=[Commit(uid='a-random-uid', message="A commit message")],
        patches=[Patch(type_=PatchClassification.BACKPORT)],
        notes='Some notes here please'
    )


def get_properties_1() -> List[Property]:
    return [
        Property(name='key1', value='val1'),
        Property(name='key2', value='val2')
    ]


def get_release_notes() -> ReleaseNotes:
    text_content: str = base64.b64encode(
        bytes('Some simple plain text', encoding='UTF-8')
    ).decode(encoding='UTF-8')

    return ReleaseNotes(
        type_='major', title="Release Notes Title",
        featured_image=XsUri('https://cyclonedx.org/theme/assets/images/CycloneDX-Twitter-Card.png'),
        social_image=XsUri('https://cyclonedx.org/cyclonedx-icon.png'),
        description="This release is a test release", timestamp=MOCK_TIMESTAMP,
        aliases=[
            "First Test Release"
        ],
        tags=['test', 'alpha'],
        resolves=[get_issue_1()],
        notes=[
            Note(
                text=NoteText(
                    content=text_content, content_type='text/plain; charset=UTF-8',
                    content_encoding=Encoding.BASE_64
                ), locale='en-GB'
            ),
            Note(
                text=NoteText(
                    content=text_content, content_type='text/plain; charset=UTF-8',
                    content_encoding=Encoding.BASE_64
                ), locale='en-US'
            )
        ],
        properties=get_properties_1()
    )


def get_swid_1() -> Swid:
    return Swid(
        tag_id='swidgen-242eb18a-503e-ca37-393b-cf156ef09691_9.1.1', name='Test Application',
        version='3.4.5', text=AttachedText(
            content='PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiID8+CjxTb2Z0d2FyZUlkZW50aXR5IHhtbDpsYW5nPSJFTiIgbm'
                    'FtZT0iQWNtZSBBcHBsaWNhdGlvbiIgdmVyc2lvbj0iOS4xLjEiIAogdmVyc2lvblNjaGVtZT0ibXVsdGlwYXJ0bnVtZXJpYyIg'
                    'CiB0YWdJZD0ic3dpZGdlbi1iNTk1MWFjOS00MmMwLWYzODItM2YxZS1iYzdhMmE0NDk3Y2JfOS4xLjEiIAogeG1sbnM9Imh0dH'
                    'A6Ly9zdGFuZGFyZHMuaXNvLm9yZy9pc28vMTk3NzAvLTIvMjAxNS9zY2hlbWEueHNkIj4gCiB4bWxuczp4c2k9Imh0dHA6Ly93'
                    'd3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiAKIHhzaTpzY2hlbWFMb2NhdGlvbj0iaHR0cDovL3N0YW5kYXJkcy'
                    '5pc28ub3JnL2lzby8xOTc3MC8tMi8yMDE1LWN1cnJlbnQvc2NoZW1hLnhzZCBzY2hlbWEueHNkIiA+CiAgPE1ldGEgZ2VuZXJh'
                    'dG9yPSJTV0lEIFRhZyBPbmxpbmUgR2VuZXJhdG9yIHYwLjEiIC8+IAogIDxFbnRpdHkgbmFtZT0iQWNtZSwgSW5jLiIgcmVnaW'
                    'Q9ImV4YW1wbGUuY29tIiByb2xlPSJ0YWdDcmVhdG9yIiAvPiAKPC9Tb2Z0d2FyZUlkZW50aXR5Pg==',
            content_type='text/xml', encoding=Encoding.BASE_64
        )
    )


def get_swid_2() -> Swid:
    return Swid(
        tag_id='swidgen-242eb18a-503e-ca37-393b-cf156ef09691_9.1.1', name='Test Application',
        version='3.4.5', url=XsUri('https://cyclonedx.org')
    )


def get_vulnerability_source_nvd() -> VulnerabilitySource:
    return VulnerabilitySource(name='NVD', url=XsUri('https://nvd.nist.gov/vuln/detail/CVE-2018-7489'))


def get_vulnerability_source_owasp() -> VulnerabilitySource:
    return VulnerabilitySource(name='OWASP', url=XsUri('https://owasp.org'))


T = TypeVar('T')


def reorder(items: List[T], indexes: List[int]) -> List[T]:
    '''
    Return list of items in the order indicated by indexes.
    '''
    reordered_items = []
    for i in range(len(items)):
        reordered_items.append(items[indexes[i]])
    return reordered_items
