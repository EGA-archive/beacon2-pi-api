# Beacon PI Release and Support Lifecycle Policy

## 1. Scope and goals

This is the document to refer to all the aspects on how Beacon PI will maintain and produce each of its releases, in order to state the procedure followed for all the stakeholders interested in this matter. 

The goals of this document are to:

- Provide transparency regarding Beacon PI releases and supported versions.
- Enable clients and integrators to plan upgrade cycles in advance.
- Define the support period and end-of-life (EOL) process for Beacon PI versions.
- Establish a clear process for critical security fixes and hotfixes.
- Align major software releases with changes to the underlying Beacon specification.

---

## 2. Lifecycle Stages

Beacon PI versions progress through the stages based on its development flow, tied to the GitHub branch management. This flow consists on having branches names according to the type of development that is being performed: fixes, features, clean-up. This is somehow an Alpha stage. When this alpha stage is good enough and the unit tests happen to pass, everything is merged into a broader branch called develop, in which all the integration tests come into action. This is a Beta stage. When this Beta stage succeeds, everything becomes ready for a new release and a production ready version of the development done, which materializes in the version upgrade.

| Stage        | Description                                                                                                      |
|--------------|------------------------------------------------------------------------------------------------------------------|
| **Alpha**    | This stage is based on particular developments focused on the new features/fixes of the software. More than one development can happen at the same time. Unit tests related to this particular new developments are executed in order to reach the beta stage. Translated to branch management, this happens in the different develop_<name_of_the_development> branches where each of the new functionalities are engineered. |
| **Beta**     | Exhaustive testing including broader unit testing of all the developments together that compose the new software candidate. Here, also integration and concurrency testing are executed to assess the new components and confirm they are not causing any unexpected behaviour to the performance. Translated to branch management, this happens in the develop branch. If this is not successful, then, additional alpha developments might be needed.  |
| **Production** | Officially released version supported for use in production environments.       |
| **End-of-Life (EOL)** | Version that is no longer supported. No further maintenance or security fixes are provided except where explicitly stated otherwise. |


---

## 3. Release Cadence

The release cadence is intended to provide regular maintenance while avoiding unnecessary disruption to users and integrators.

### 3.1 Major Releases

A major release is associated with a complete new major version of the Beacon specification.

The first version of the Beacon spec took place in 2015, where Beacon v1 was released. This was followed by Beacon v2 release, that happened in 2022. A new Beacon v3 is now planned to be released, which will make Beacon PI have the need to make a major release to have its version also adapted to the new specification version. This will take some time, but on average, the major relases happen **between 5-7 years**.

A major release may introduce:

- Breaking changes.
- Architectural/component changes.
- Additional non-breaking but subtle changes

> The five to seven-year period is an expected cadence rather than a strict release deadline. The actual timing may depend on the availability and maturity of the Beacon specification.

### 3.2 Minor and Maintenance Releases

Between major releases, minor and maintenance releases may be issued as needed to provide:

- Bug fixes.
- Security fixes.
- Compatibility improvements.
- Performance and reliability improvements.
- Documentation updates.
- Other non-breaking improvements.

The exact frequency of minor and maintenance releases is determined by operational and development requirements rather than by a fixed calendar commitment.

---

## 4. Support Period

Each **Production** major release is supported for **12 months** at least from its initial Production release date.

It is expected that Beacon PI supports all the Beacon versions from version 2 onwards, providing support for the officially released schemas of each version of the specification. Nonetheless, the 12 months period will be used for declaring a version End of life (EOL), which means, support may happen but it is not guaranteed.

During the support period, the project will provide reasonable maintenance for the supported release, including applicable:

- Security fixes.
- Critical and significant bug fixes.
- Compatibility fixes where appropriate.
- Documentation relating to supported functionality.

> Support does not necessarily mean that every reported issue will result in a code change. Issues may instead be addressed through configuration guidance, documentation, workarounds, or an upgrade recommendation.

---

## 5. End-of-Life (EOL)

At the end of the 12-month support period, a major release reaches **End-of-Life (EOL)**.

After EOL:

- The version is no longer officially supported.
- Regular bug fixes and security fixes may no longer be provided.
- New functionality may not be backported to the EOL version.
- Users and integrators should migrate to a currently supported release.
- EOL dates for Production releases will be publicly documented to allow stakeholders to plan upgrades.

Where practical, EOL notifications will be communicated sufficiently in advance of the EOL date.

---

## 6. Critical Security Vulnerabilities and Hotfixes

Critical security vulnerabilities may require an immediate release outside the normal release cadence.

When a critical vulnerability affecting a supported Production version is identified and a fix is available, a security hotfix may be issued without waiting for the next scheduled maintenance release.

Security hotfixes may:

- Be released independently of the normal release schedule.
- Contain only the changes necessary to address the vulnerability and associated risks.
- Apply to one or more currently supported versions, where technically feasible.
- Be accompanied by security advisories or release notes describing the affected versions and required actions.

The availability and scope of a hotfix will depend on:

- The severity of the vulnerability.
- The affected components.
- Technical feasibility.
- The versions still within their support period.

> EOL versions are generally not eligible for security hotfixes.

---

## 7. Version Compatibility and Upgrades

Users and integrators are responsible for planning upgrades before the supported version reaches EOL.

Where a major release introduces breaking changes, migration documentation should be provided to assist users in moving from the previous supported version.

> Integrators should avoid building dependencies on undocumented or explicitly unstable interfaces, particularly in Alpha and Beta releases.

---

## 8. Publication of Lifecycle Information

The following information will be maintained in the official documentation:

- Current Production release.
- Supported major versions.
- Initial Production release date for each major version.
- Support major version end date.
- Major version EOL date.
- Relevant release and security notices.
- Upgrade and migration guidance where applicable.

---

## 9. Lifecycle Overview

```text
Beacon PI Development version X <----- Specification development reaches new major version X+1
          |
          v
        Alpha
          |
          v
         Beta
          |
          v
      Production ----------------------------->  Beacon PI new version X+1
          | version X                                       |
          | 12 months of support                            v
          v                                                Alpha
         EOL                                                |
                                                            v
                                                           Beta
                                                            |
                                                            v
                                                        Production
```

- Major Production releases are expected to correspond to significant specification revisions and are expected approximately every **7 years**, approximately.
- Each Production major release has an independent **12-month** support period.

---

## 10. Policy Changes

This policy may be revised to reflect changes in:

- The Beacon specification.
- Project governance.
- Security requirements.
- Operational constraints.
- User and integrator requirements.

Material changes to the support lifecycle will be documented and communicated through the official project documentation.